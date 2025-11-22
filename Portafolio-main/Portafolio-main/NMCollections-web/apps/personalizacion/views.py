from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import os
from .models import (
    Plantilla, PlantillaElemento, PlantillaFondo,
    CartaPersonalizada, CartaParametro
)
from .serializers import (
    PlantillaSerializer, PlantillaElementoSerializer, PlantillaFondoSerializer,
    CartaPersonalizadaSerializer, CartaParametroSerializer
)
from .services import RecorteInteligenteService, RecorteUtils
from apps.pedidos.models import Pedido, PedidoProducto
from apps.productos.models import Producto, CategoriaProducto
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import ModelForm, forms
from django import forms as django_forms

class PlantillaForm(ModelForm):
    class Meta:
        model = Plantilla
        fields = ['nombre', 'descripcion', 'tipo_carta', 'imagen_marco', 'ancho_marco', 'alto_marco', 'diseñador']
        widgets = {
            'nombre': django_forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la plantilla'
            }),
            'descripcion': django_forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la plantilla'
            }),
            'tipo_carta': django_forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de carta (ej: pokemon, yugioh, magic)'
            }),
            'imagen_marco': django_forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'ancho_marco': django_forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '100',
                'max': '1000'
            }),
            'alto_marco': django_forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '100',
                'max': '1000'
            }),
            'diseñador': django_forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del diseñador'
            })
        }

class PlantillaElementoForm(ModelForm):
    class Meta:
        model = PlantillaElemento
        fields = ['nombre_parametro', 'tipo_elemento', 'posicion_x', 'posicion_y', 
                 'ancho', 'alto', 'fuente', 'color', 'z_index']
        widgets = {
            'nombre_parametro': django_forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del parámetro'
            }),
            'tipo_elemento': django_forms.Select(attrs={'class': 'form-control'}),
            'posicion_x': django_forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'posicion_y': django_forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ancho': django_forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'alto': django_forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'fuente': django_forms.TextInput(attrs={'class': 'form-control'}),
            'color': django_forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'z_index': django_forms.NumberInput(attrs={'class': 'form-control'})
        }

@staff_member_required
def panel_diseñador(request):
    """Panel principal para diseñadores - solo para staff"""
    plantillas = Plantilla.objects.all().order_by('-fecha_creacion')
    return render(request, 'personalizacion/panel_diseñador.html', {
        'plantillas': plantillas
    })

@staff_member_required
def crear_plantilla(request):
    """Crear nueva plantilla"""
    if request.method == 'POST':
        form = PlantillaForm(request.POST, request.FILES)
        if form.is_valid():
            plantilla = form.save(commit=False)
            plantilla.usuario_creador = request.user
            plantilla.save()
            messages.success(request, f'Plantilla "{plantilla.nombre}" creada exitosamente')
            return redirect('personalizacion:panel_diseñador')
    else:
        form = PlantillaForm()
    
    return render(request, 'personalizacion/crear_plantilla.html', {
        'form': form
    })

@staff_member_required
def editar_plantilla(request, plantilla_id):
    """Editar plantilla existente"""
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    if request.method == 'POST':
        form = PlantillaForm(request.POST, request.FILES, instance=plantilla)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plantilla "{plantilla.nombre}" actualizada exitosamente')
            return redirect('personalizacion:panel_diseñador')
    else:
        form = PlantillaForm(instance=plantilla)
    
    elementos = PlantillaElemento.objects.filter(plantilla=plantilla)
    
    return render(request, 'personalizacion/editar_plantilla.html', {
        'form': form,
        'plantilla': plantilla,
        'elementos': elementos
    })

@staff_member_required
def eliminar_plantilla(request, plantilla_id):
    """Eliminar plantilla"""
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    if request.method == 'POST':
        nombre = plantilla.nombre
        plantilla.delete()
        messages.success(request, f'Plantilla "{nombre}" eliminada exitosamente')
        return redirect('personalizacion:panel_diseñador')
    
    return render(request, 'personalizacion/confirmar_eliminar_plantilla.html', {
        'plantilla': plantilla
    })

@staff_member_required
def agregar_elemento(request, plantilla_id):
    """Agregar elemento a plantilla"""
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    if request.method == 'POST':
        form = PlantillaElementoForm(request.POST)
        if form.is_valid():
            elemento = form.save(commit=False)
            elemento.plantilla = plantilla
            elemento.save()
            messages.success(request, f'Elemento "{elemento.nombre_parametro}" agregado exitosamente')
            return redirect('personalizacion:editar_plantilla', plantilla_id=plantilla.id)
    else:
        form = PlantillaElementoForm()
    
    return render(request, 'personalizacion/agregar_elemento.html', {
        'form': form,
        'plantilla': plantilla
    })

@staff_member_required
def eliminar_elemento(request, elemento_id):
    """Eliminar elemento de plantilla"""
    elemento = get_object_or_404(PlantillaElemento, id=elemento_id)
    plantilla_id = elemento.plantilla.id
    
    if request.method == 'POST':
        nombre = elemento.nombre_parametro
        elemento.delete()
        messages.success(request, f'Elemento "{nombre}" eliminado exitosamente')
        return redirect('personalizacion:editar_plantilla', plantilla_id=plantilla_id)
    
    return render(request, 'personalizacion/confirmar_eliminar_elemento.html', {
        'elemento': elemento
    })

@login_required
def mis_cartas(request):
    """
    Vista para mostrar todas las cartas del usuario (borradores y finalizadas)
    Con funcionalidad completa de gestión
    """
    print(f"🔍 DEBUG: Usuario actual: {request.user}")
    print(f"🔍 DEBUG: Usuario ID: {request.user.id}")
    print(f"🔍 DEBUG: ¿Está autenticado?: {request.user.is_authenticated}")
    
    # Usar la misma lógica que perfil_cartas para consistencia
    borradores = CartaPersonalizada.objects.filter(
        usuario=request.user, 
        estado__in=['borrador', 'en_edicion']  # Aceptar ambos estados como perfil
    ).order_by('-fecha_creacion')
    
    finalizadas = CartaPersonalizada.objects.filter(
        usuario=request.user, 
        estado='finalizada'
    ).order_by('-fecha_creacion')
    
    print(f"🔍 DEBUG: Borradores encontrados: {borradores.count()}")
    print(f"🔍 DEBUG: Finalizadas encontradas: {finalizadas.count()}")
    
    for borrador in borradores:
        print(f"   📄 Borrador: {borrador.nombre_carta} (ID: {borrador.id})")
    
    context = {
        'borradores': borradores,
        'finalizadas': finalizadas,
    }
    return render(request, 'personalizacion/mis_cartas.html', context)

@login_required
def editar_carta(request, carta_id):
    """
    Vista para editar una carta existente
    """
    carta = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user)
    
    # Solo se pueden editar cartas en estado 'en_edicion'
    if carta.estado != 'en_edicion':
        messages.error(request, 'Esta carta ya no se puede editar')
        return redirect('personalizacion:mis_cartas')
    
    # Redirigir al canvas editor con la carta pre-cargada
    return redirect(f'/personalizacion/canvas-editor/?carta_id={carta_id}')

@login_required
def finalizar_carta(request, carta_id):
    """
    Vista para finalizar una carta (cambiar de borrador a finalizada)
    SIN generar pedido automáticamente
    """
    if request.method == 'POST':
        carta = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user)
        
        if carta.estado == 'en_edicion':
            carta.estado = 'finalizada'
            carta.save()
            
            mensaje_exito = 'Carta finalizada exitosamente. Ahora puedes crear un pedido desde "Mis Cartas".'
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': mensaje_exito,
                    'carta_id': carta.id
                })
            else:
                messages.success(request, mensaje_exito)
                
        else:
            mensaje_error = 'Esta carta ya está finalizada'
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': mensaje_error
                }, status=400)
            else:
                messages.error(request, mensaje_error)
    
    # Si no es AJAX, redirigir normalmente
    return redirect('personalizacion:mis_cartas')

@login_required
def eliminar_carta(request, carta_id):
    """
    Vista para eliminar una carta
    """
    if request.method == 'POST':
        carta = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user)
        carta.delete()
        messages.success(request, 'Carta eliminada exitosamente')
    
    return redirect('personalizacion:mis_cartas')

class PlantillaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar plantillas disponibles
    """
    queryset = Plantilla.objects.filter(estado='activa')
    serializer_class = PlantillaSerializer
    
    @action(detail=True, methods=['get'])
    def elementos(self, request, pk=None):
        """
        Obtener todos los elementos de una plantilla específica
        """
        plantilla = self.get_object()
        elementos = PlantillaElemento.objects.filter(plantilla=plantilla).order_by('z_index')
        serializer = PlantillaElementoSerializer(elementos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def fondo(self, request, pk=None):
        """
        Obtener el fondo de una plantilla específica
        """
        plantilla = self.get_object()
        try:
            fondo = PlantillaFondo.objects.get(plantilla=plantilla)
            serializer = PlantillaFondoSerializer(fondo)
            return Response(serializer.data)
        except PlantillaFondo.DoesNotExist:
            return Response({'error': 'Fondo no encontrado'}, status=404)

class CartaPersonalizadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de cartas personalizadas
    """
    serializer_class = CartaPersonalizadaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartaPersonalizada.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def actualizar_parametros(self, request, pk=None):
        """
        Actualizar parámetros de una carta en tiempo real
        """
        carta = self.get_object()
        parametros_data = request.data.get('parametros', [])
        
        # Eliminar parámetros existentes
        CartaParametro.objects.filter(carta=carta).delete()
        
        # Crear nuevos parámetros
        parametros_creados = []
        for param_data in parametros_data:
            parametro = CartaParametro.objects.create(
                carta=carta,
                **param_data
            )
            parametros_creados.append(parametro)
        
        # Actualizar estado de la carta
        carta.estado = request.data.get('estado', 'borrador')
        carta.save()
        
        serializer = CartaParametroSerializer(parametros_creados, many=True)
        return Response({
            'message': 'Parámetros actualizados exitosamente',
            'parametros': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """
        Finalizar la edición de una carta
        """
        carta = self.get_object()
        carta.estado = 'finalizada'
        carta.save()
        
        serializer = self.get_serializer(carta)
        return Response({
            'message': 'Carta finalizada exitosamente',
            'carta': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def crear_pedido(self, request, pk=None):
        """
        Crear un pedido a partir de una carta finalizada
        """
        carta = self.get_object()
        
        if carta.estado != 'finalizada':
            return Response({
                'error': 'Solo se pueden crear pedidos de cartas finalizadas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.pedidos.models import Pedido, PedidoProducto
            from apps.productos.models import Producto
            
            # Buscar producto de trading card que corresponda al tipo de carta
            producto_carta = None
            tipo_carta = carta.plantilla.tipo_carta
            
            # Mapear tipos de carta a productos
            tipo_a_producto = {
                'futbol_clasica': 'Trading Card Personalizada - Deportes',
                'anime_ninja': 'Trading Card Personalizada - Anime', 
                'gaming_pro': 'Trading Card Personalizada - Gaming',
                'retro_deportiva': 'Trading Card Personalizada - Deportes'
            }
            
            if tipo_carta in tipo_a_producto:
                producto_carta = Producto.objects.filter(
                    nombre=tipo_a_producto[tipo_carta]
                ).first()
            
            if not producto_carta:
                # Usar el primer producto de cartas disponible
                producto_carta = Producto.objects.filter(
                    categoria__nombre__icontains='Trading Card'
                ).first()
            
            if not producto_carta:
                return Response({
                    'error': 'No se encontró un producto para este tipo de carta'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear el pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                estado='pendiente'
            )
            
            # Preparar datos de personalización para JSON
            parametros = CartaParametro.objects.filter(carta=carta)
            personalizacion_data = {
                'carta_id': carta.id,
                'carta_nombre': carta.nombre_carta,
                'plantilla': {
                    'id': carta.plantilla.id,
                    'nombre': carta.plantilla.nombre,
                    'tipo': carta.plantilla.tipo_carta
                },
                'parametros': [
                    {
                        'nombre': param.nombre_parametro,
                        'tipo': param.tipo_parametro,
                        'valor': param.valor
                    } for param in parametros
                ]
            }
            
            # Crear el producto en el pedido
            pedido_producto = PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto_carta,
                cantidad=1,
                personalizacion=personalizacion_data,
                precio_total=producto_carta.precio_base
            )
            
            # Calcular total del pedido
            pedido.calcular_total()
            
            return Response({
                'message': 'Pedido creado exitosamente',
                'pedido_id': pedido.id,
                'numero_pedido': pedido.numero_pedido,
                'total': float(pedido.total),
                'producto': producto_carta.nombre
            })
            
        except Exception as e:
            return Response({
                'error': f'Error creando pedido: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Generar preview de la carta para el canvas
        """
        carta = self.get_object()
        parametros = CartaParametro.objects.filter(carta=carta)
        
        carta_data = {
            'id': carta.id,
            'nombre': carta.nombre_carta,
            'plantilla': PlantillaSerializer(carta.plantilla).data,
            'parametros': CartaParametroSerializer(parametros, many=True).data,
            'estado': carta.estado
        }
        
        return Response(carta_data)

class CanvasEditorView(viewsets.ViewSet):
    """
    ViewSet específico para el editor de canvas
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def plantillas_disponibles(self, request):
        """
        Obtener todas las plantillas disponibles para el canvas
        NOTA: No requiere autenticación para permitir que cualquier usuario vea las plantillas
        """
        plantillas = Plantilla.objects.filter(estado='activa')
        data = []
        
        for plantilla in plantillas:
            elementos = PlantillaElemento.objects.filter(plantilla=plantilla).order_by('z_index')
            fondo = PlantillaFondo.objects.filter(plantilla=plantilla).first()
            
            plantilla_data = {
                'id': plantilla.id,
                'nombre': plantilla.nombre,
                'descripcion': plantilla.descripcion,
                'tipo_carta': plantilla.tipo_carta,
                'imagen_preview': plantilla.imagen_preview,
                'imagen_marco_url': plantilla.imagen_marco.url if plantilla.imagen_marco else None,
                'ancho_marco': plantilla.ancho_marco,
                'alto_marco': plantilla.alto_marco,
                'diseñador': plantilla.diseñador,
                'archivo_original': plantilla.archivo_original,
                'elementos': PlantillaElementoSerializer(elementos, many=True).data,
                'fondo': PlantillaFondoSerializer(fondo).data if fondo else None
            }
            data.append(plantilla_data)
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def guardar_carta_temporal(self, request):
        """
        Guardar carta en estado temporal mientras se edita
        """
        try:
            plantilla_id = request.data.get('plantilla_id')
            nombre_carta = request.data.get('nombre_carta', 'Mi Carta Personalizada')
            parametros = request.data.get('parametros', [])
            
            # Validar datos requeridos
            if not plantilla_id:
                return Response({
                    'error': 'plantilla_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                plantilla = Plantilla.objects.get(id=plantilla_id)
            except Plantilla.DoesNotExist:
                return Response({
                    'error': f'Plantilla con ID {plantilla_id} no existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear nueva carta temporal (siempre crear nueva, no reutilizar)
            carta = CartaPersonalizada.objects.create(
                usuario=request.user,
                plantilla=plantilla,
                estado='en_edicion',
                nombre_carta=nombre_carta
            )
            
            # Actualizar parámetros
            CartaParametro.objects.filter(carta=carta).delete()
            for param_data in parametros:
                if isinstance(param_data, dict):
                    # Validar que los campos requeridos están presentes
                    if 'nombre_parametro' in param_data and 'valor' in param_data:
                        CartaParametro.objects.create(
                            carta=carta,
                            nombre_parametro=param_data.get('nombre_parametro'),
                            tipo_parametro=param_data.get('tipo_parametro', 'texto'),
                            valor=param_data.get('valor', '')
                        )
            
            return Response({
                'message': 'Carta guardada temporalmente',
                'carta_id': carta.id,
                'status': 'success'
            })
            
        except Exception as e:
            import traceback
            print(f"Error en guardar_carta_temporal: {str(e)}")
            print(traceback.format_exc())
            return Response({
                'error': f'Error interno: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def recorte_inteligente(self, request):
        """
        Aplica recorte inteligente a una imagen subida
        """
        try:
            # Verificar que se subió un archivo
            if 'imagen' not in request.FILES:
                return Response({
                    'error': 'No se proporcionó ninguna imagen'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            archivo_imagen = request.FILES['imagen']
            
            # Verificar que es una imagen válida
            if not RecorteUtils.es_imagen_valida(archivo_imagen):
                return Response({
                    'error': 'El archivo debe ser una imagen válida (JPG, PNG, BMP, TIFF)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener parámetros opcionales
            tipo_elemento = request.data.get('tipo_elemento', 'foto_jugador')
            ancho, alto = RecorteUtils.obtener_dimensiones_recomendadas(tipo_elemento)
            
            # Parámetros personalizados si se proporcionan
            ancho = int(request.data.get('ancho', ancho))
            alto = int(request.data.get('alto', alto))
            
            # Guardar archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in archivo_imagen.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Procesar imagen con recorte inteligente
                imagen_procesada, imagen_bytes = RecorteInteligenteService.procesar_imagen_completa(
                    temp_path, ancho, alto
                )
                
                if imagen_procesada is None:
                    return Response({
                        'error': 'No se pudo procesar la imagen. Intenta con otra imagen.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Generar nombre único para la imagen procesada
                nombre_original = archivo_imagen.name
                nombre_base = os.path.splitext(nombre_original)[0]
                nombre_procesado = f"{nombre_base}_recortado_{request.user.id}.png"
                
                # Guardar imagen procesada
                ruta_guardada = RecorteInteligenteService.guardar_imagen_procesada(
                    imagen_bytes, nombre_procesado
                )
                
                if ruta_guardada:
                    # Construir URL completa
                    url_imagen = default_storage.url(ruta_guardada)
                    
                    return Response({
                        'message': 'Imagen procesada exitosamente',
                        'imagen_original': archivo_imagen.name,
                        'imagen_procesada': nombre_procesado,
                        'url_imagen_procesada': url_imagen,
                        'dimensiones': {
                            'ancho': ancho,
                            'alto': alto
                        },
                        'tipo_elemento': tipo_elemento
                    })
                else:
                    return Response({
                        'error': 'Error guardando la imagen procesada'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return Response({
                'error': f'Error procesando imagen: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Vista para renderizar el editor de canvas (REQUIERE LOGIN)
@login_required
def canvas_editor(request):
    """
    Vista para mostrar el editor de canvas - SOLO usuarios autenticados
    """
    return render(request, 'personalizacion/canvas_editor.html')

# Vista para el perfil con borradores
@login_required
def perfil_cartas(request):
    """
    Vista para mostrar las cartas del usuario en su perfil
    """
    cartas_borrador = CartaPersonalizada.objects.filter(
        usuario=request.user, 
        estado__in=['borrador', 'en_edicion']  # Aceptar ambos estados
    ).order_by('-fecha_creacion')
    
    cartas_finalizadas = CartaPersonalizada.objects.filter(
        usuario=request.user, 
        estado='finalizada'
    ).order_by('-fecha_creacion')
    
    print(f"🔍 DEBUG perfil_cartas: Borradores: {cartas_borrador.count()}")
    print(f"🔍 DEBUG perfil_cartas: Finalizadas: {cartas_finalizadas.count()}")
    
    context = {
        'cartas_borrador': cartas_borrador,
        'cartas_finalizadas': cartas_finalizadas,
    }
    return render(request, 'personalizacion/perfil_cartas.html', context)


# Nuevas vistas para funcionalidad de mis-cartas
from django.http import JsonResponse
from django.core.files.base import ContentFile
import base64
import uuid

@login_required
def vista_previa_carta(request, carta_id):
    """
    Vista para mostrar la previa de una carta
    """
    carta = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user)
    
    context = {
        'carta': carta,
    }
    return render(request, 'personalizacion/vista_previa_carta.html', context)

@login_required
def crear_pedido_carta(request, carta_id):
    """
    API para crear un pedido a partir de una carta finalizada
    """
    if request.method == 'POST':
        carta = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user)
        
        if carta.estado != 'finalizada':
            return JsonResponse({'success': False, 'error': 'Solo se pueden comprar cartas finalizadas'})
        
        try:
            # Importar modelos necesarios
            from apps.productos.models import CategoriaProducto, Producto
            from apps.pedidos.models import Pedido, PedidoProducto
            
            # Verificar si ya existe un pedido para esta carta
            pedido_existente = PedidoProducto.objects.filter(carta_personalizada=carta).first()
            if pedido_existente:
                return JsonResponse({
                    'success': False, 
                    'error': f'Ya existe un pedido para esta carta (Pedido #{pedido_existente.pedido.numero_pedido})'
                })
            
            # Obtener o crear una categoría por defecto para cartas
            categoria_carta, created = CategoriaProducto.objects.get_or_create(
                nombre='Carta Personalizada',
                defaults={
                    'descripcion': 'Cartas personalizadas de trading'
                }
            )
            
            # Crear un producto único para esta carta
            # Usar un identificador único para evitar duplicados
            producto_carta = Producto.objects.create(
                nombre=f"Carta Personalizada #{carta.id} - {carta.nombre_carta or 'Personalizada'}",
                descripcion=f"Carta personalizada basada en plantilla {carta.plantilla.nombre}",
                precio_base=15000,
                categoria=categoria_carta,
                tipo='personalizado',
                estado='Inactivo',
                imagen_referencia=carta.imagen_generada if carta.imagen_generada else None
            )
            
            # Crear pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                estado='pendiente',
                metodo_pago='pendiente',
                notas=f'Pedido para la carta "{carta.nombre_carta}"'
            )
            
            # Agregar producto al pedido con relación directa a la carta
            pedido_producto = PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto_carta,
                cantidad=1,
                carta_personalizada=carta,  # Nueva relación directa
                personalizacion={
                    'carta_id': carta.id,
                    'plantilla': carta.plantilla.nombre,
                    'parametros': [
                        {
                            'nombre': param.nombre_parametro,
                            'valor': param.valor
                        } for param in carta.cartaparametro_set.all()
                    ]
                },
                precio_total=producto_carta.precio_base
            )
            
            # Calcular total del pedido
            pedido.calcular_total()
            
            # Marcar carta como comprada
            carta.estado = 'comprada'
            carta.save()
            
            return JsonResponse({
                'success': True, 
                'pedido_id': pedido.id,
                'message': f'Pedido #{pedido.numero_pedido} creado exitosamente por ${pedido.total:,.0f}'
            })
            
        except Exception as e:
            import traceback
            print(f"Error en crear_pedido_carta: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def duplicar_carta(request, carta_id):
    """
    API para duplicar una carta como nuevo borrador
    """
    if request.method == 'POST':
        carta_original = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user)
        
        try:
            # Crear nueva carta duplicada
            nueva_carta = CartaPersonalizada.objects.create(
                usuario=request.user,
                plantilla=carta_original.plantilla,
                nombre_carta=f"{carta_original.nombre_carta} (Copia)",
                estado='en_edicion',
                imagen_generada=carta_original.imagen_generada
            )
            
            # Duplicar parámetros
            for param in carta_original.cartaparametro_set.all():
                CartaParametro.objects.create(
                    carta=nueva_carta,
                    nombre_parametro=param.nombre_parametro,
                    valor=param.valor
                )
            
            return JsonResponse({'success': True, 'carta_id': nueva_carta.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required  
def guardar_imagen_carta(request, carta_id):
    """
    Vista API para guardar la imagen PNG generada del canvas
    """
    if request.method == 'POST':
        try:
            carta = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user)
            
            # Obtener la imagen en base64 del POST
            imagen_data = request.POST.get('imagen_data')
            if not imagen_data:
                return JsonResponse({'success': False, 'error': 'No se proporcionó imagen'})
            
            # Remover el prefijo data:image/png;base64,
            if imagen_data.startswith('data:image/png;base64,'):
                imagen_data = imagen_data.split(',')[1]
            
            # Decodificar la imagen
            imagen_binaria = base64.b64decode(imagen_data)
            
            # Crear archivo con nombre único
            nombre_archivo = f"carta_{carta.id}_{uuid.uuid4().hex[:8]}.png"
            archivo_imagen = ContentFile(imagen_binaria, nombre_archivo)
            
            # Guardar en el campo imagen_generada
            carta.imagen_generada.save(nombre_archivo, archivo_imagen, save=True)
            # Guardar la ruta en el campo ruta_imagen
            carta.ruta_imagen = carta.imagen_generada.name
            carta.save(update_fields=["ruta_imagen"])
            return JsonResponse({
                'success': True, 
                'imagen_url': carta.imagen_generada.url,
                'message': 'Imagen guardada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
