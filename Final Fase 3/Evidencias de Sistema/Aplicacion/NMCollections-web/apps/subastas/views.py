from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta

from .models import Subasta, Puja, MensajeSubasta
from .forms import SubastaForm


def eliminar_subasta(request, subasta_id):
    subasta = get_object_or_404(Subasta, id=subasta_id)
    nombre_producto = subasta.producto.nombre
    subasta.delete()
    messages.success(request, f"La subasta de '{nombre_producto}' fue eliminada correctamente.")
    return redirect('subastas:subasta')

@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class SubastaAdminView(LoginRequiredMixin, View):
    template_name = 'subastas/admin_subastas.html'

    def get(self, request):
        subastas = Subasta.objects.select_related('producto').order_by('-fecha_inicio')
        form = SubastaForm()
        return render(request, self.template_name, {
            'form': form,
            'subastas': subastas,
        })

    def post(self, request):
        form = SubastaForm(request.POST, request.FILES)
        if form.is_valid():
            subasta = form.save()
            messages.success(request, f"Subasta de '{subasta.producto.nombre}' creada correctamente.")
            return redirect('subastas:admin_subastas')
        subastas = Subasta.objects.select_related('producto').order_by('-fecha_inicio')
        return render(request, self.template_name, {'form': form, 'subastas': subastas})

class SubastaView(LoginRequiredMixin, TemplateView):
    template_name = 'subastas/subastas.html'
    def get(self, request, *args, **kwargs):
        ahora = timezone.now()
        limite_eliminacion = ahora - timedelta(days=2)

        # --- 1) Elimina subastas viejas ---
        Subasta.objects.filter(fecha_fin__lt=limite_eliminacion).delete()

        # --- 2) Carga subastas vigentes ---
        subastas = Subasta.objects.select_related('producto').filter(
            fecha_fin__gte=limite_eliminacion
        ).order_by('-fecha_inicio')[:36]

        # --- 3) ACTUALIZA estados automáticamente ---
        for s in subastas:
            s.actualizar_estado()  # <- usa el método del modelo

        # --- 4) Muestra el formulario solo si el usuario es staff ---
        form = SubastaForm() if request.user.is_staff else None

        return self.render_to_response({
            'form': form,
            'subastas': subastas,
        })

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse('subastas:subasta'))

        form = SubastaForm(request.POST)
        if form.is_valid():
            subasta = form.save()
            return redirect(reverse('subastas:subasta'))

        # Recalcular subastas (por si se eliminaron)
        ahora = timezone.now()
        limite_eliminacion = ahora - timedelta(days=2)
        subastas = Subasta.objects.select_related('producto').filter(
            fecha_fin__gte=limite_eliminacion
        ).order_by('-fecha_inicio')[:36]

        # También actualiza estados en POST
        for s in subastas:
            s.actualizar_estado()

        return self.render_to_response({
            'form': form,
            'subastas': subastas,
        })

class SubastaDetalleView(LoginRequiredMixin, View):
    template_name = 'subastas/detalle_subasta.html'

    def get(self, request, subasta_id):
        subasta = get_object_or_404(Subasta.objects.select_related('producto'), id=subasta_id)
        # Limita aquí a las últimas 3 pujas
        pujas = subasta.pujas.select_related('usuario').order_by('-fecha')[:3]

        return render(request, self.template_name, {
            'subasta': subasta,
            'pujas': pujas,
        })

    def post(self, request, subasta_id):
        subasta = get_object_or_404(Subasta, id=subasta_id)

        try:
            monto = float(request.POST.get('monto'))
        except (TypeError, ValueError):
            messages.error(request, "Monto inválido.")
            return redirect('subastas:detalle', subasta_id=subasta.id)

        puede_pujar, mensaje = subasta.puede_pujar(request.user, monto)
        if not puede_pujar:
            messages.error(request, mensaje)
            return redirect('subastas:detalle', subasta_id=subasta.id)

        # Crear la puja
        Puja.objects.create(
            subasta=subasta,
            usuario=request.user,
            monto=monto,
            ip_origen=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f"Puja de ${monto} registrada correctamente.")
        return redirect('subastas:detalle', subasta_id=subasta.id)


# ==========================================
# API ENDPOINTS - Reemplazo de WebSockets
# ==========================================

@login_required
@require_http_methods(["GET"])
def api_obtener_pujas(request, subasta_id):
    """
    API para obtener las últimas pujas de una subasta
    Reemplaza la funcionalidad de WebSocket para actualización de pujas
    """
    try:
        subasta = get_object_or_404(Subasta, id=subasta_id)
        
        # Obtener las últimas 3 pujas
        pujas = subasta.pujas.select_related('usuario').order_by('-fecha')[:3]
        
        pujas_data = [{
            'id': puja.id,
            'usuario': puja.usuario.username,
            'monto': float(puja.monto),
            'fecha': puja.fecha.strftime("%d/%m/%Y %H:%M:%S"),
        } for puja in pujas]
        
        return JsonResponse({
            'success': True,
            'pujas': pujas_data,
            'precio_actual': float(subasta.precio_actual),
            'total_pujas': subasta.total_pujas,
            'esta_activa': subasta.esta_activa,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def api_obtener_mensajes(request, subasta_id):
    """
    API para obtener mensajes de chat de una subasta
    Reemplaza la funcionalidad de WebSocket para chat
    """
    try:
        print(f"[DEBUG] Obteniendo mensajes para subasta {subasta_id}")
        subasta = get_object_or_404(Subasta, id=subasta_id)
        
        # Obtener últimos 50 mensajes
        mensajes = subasta.mensajes.select_related('usuario').order_by('-fecha')[:50]
        
        print(f"[DEBUG] Encontrados {mensajes.count()} mensajes")
        
        mensajes_data = [{
            'id': mensaje.id,
            'usuario': mensaje.usuario.username,
            'mensaje': mensaje.mensaje,
            'fecha': mensaje.fecha.strftime("%d/%m/%Y %H:%M:%S"),
        } for mensaje in reversed(mensajes)]  # Invertir para orden cronológico
        
        print(f"[DEBUG] Retornando {len(mensajes_data)} mensajes")
        
        return JsonResponse({
            'success': True,
            'mensajes': mensajes_data,
        })
    except Exception as e:
        print(f"[ERROR] Error al obtener mensajes: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_enviar_mensaje(request, subasta_id):
    """
    API para enviar un mensaje al chat de una subasta
    Reemplaza la funcionalidad de WebSocket para envío de mensajes
    """
    try:
        print(f"[DEBUG] Enviando mensaje a subasta {subasta_id}")
        print(f"[DEBUG] Usuario: {request.user.username}")
        
        subasta = get_object_or_404(Subasta, id=subasta_id)
        
        mensaje_texto = request.POST.get('mensaje', '').strip()
        
        print(f"[DEBUG] Mensaje: '{mensaje_texto}'")
        
        if not mensaje_texto:
            print(f"[ERROR] Mensaje vacío")
            return JsonResponse({
                'success': False,
                'error': 'El mensaje no puede estar vacío'
            }, status=400)
        
        # Crear mensaje
        mensaje = MensajeSubasta.objects.create(
            subasta=subasta,
            usuario=request.user,
            mensaje=mensaje_texto
        )
        
        print(f"[DEBUG] Mensaje creado con ID {mensaje.id}")
        
        return JsonResponse({
            'success': True,
            'mensaje': {
                'id': mensaje.id,
                'usuario': mensaje.usuario.username,
                'mensaje': mensaje.mensaje,
                'fecha': mensaje.fecha.strftime("%d/%m/%Y %H:%M:%S"),
            }
        })
    except Exception as e:
        print(f"[ERROR] Error al enviar mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

