from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.contrib import messages
from datetime import datetime, timedelta
import logging
from .models import Pedido, PedidoProducto, HistorialEstadoPedido
from apps.carrito.models import Carrito
from apps.productos.models import Producto
from apps.core.models import EstadoPedidoChoices
logger = logging.getLogger(__name__)
def crear_carta_view(request):
    """Vista legacy - mantener por compatibilidad"""
    return render(request, 'crearcarta/menu-crear.html')
def es_staff(user):
    """Verificar que el usuario sea staff"""
    return user.is_staff

@login_required
@require_http_methods(["POST"])
def comprar_producto(request, producto_id):
    """
    Compra directa de un producto desde el catálogo
    """
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        direccion_envio = request.POST.get('direccion_envio', '').strip()
        if not direccion_envio:
            return HttpResponseBadRequest('Debe ingresar una dirección de envío.')
        if producto.stock is not None and producto.stock < cantidad:
            return HttpResponseBadRequest('No hay suficiente stock disponible.')
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                fecha_pedido=timezone.now(),
                estado=EstadoPedidoChoices.PENDIENTE,
                direccion_envio=direccion_envio
            )
            if hasattr(producto, 'imagen_referencia') and producto.imagen_referencia:
                personalizacion = {
                    'imagen': producto.imagen_referencia.url,
                    'producto_id': producto.id,
                    'nombre_producto': producto.nombre
                }
            else:
                personalizacion = None
            PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_total=producto.precio_base * cantidad,
                personalizacion=personalizacion
            )
            pedido.calcular_total()
            if producto.stock is not None:
                producto.stock -= cantidad
                producto.save()
            
            # Enviar correo con voucher
            from apps.pedidos.emails import enviar_voucher_pedido
            enviar_voucher_pedido(pedido)
        
        messages.success(request, f'Compra realizada exitosamente. Pedido #{pedido.numero_pedido}')
        return redirect('pedidos:detalle_pedido', numero_pedido=pedido.numero_pedido)
    except Exception as e:
        logger.error(f"Error al comprar producto: {str(e)}")
        messages.error(request, 'Error al procesar la compra')
        return redirect('productos:detalle', producto_id=producto_id)
@login_required
@require_http_methods(["POST"])
def comprar_carrito(request):
    """
    Compra todos los productos del carrito
    """
    try:
        carrito = Carrito.objects.filter(usuario=request.user, estado='activo').first()
        if not carrito or not carrito.productos.exists():
            return HttpResponseBadRequest('El carrito está vacío.')
        direccion_envio = request.POST.get('direccion_envio', '').strip()
        if not direccion_envio:
            return HttpResponseBadRequest('Debe ingresar una dirección de envío.')
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                fecha_pedido=timezone.now(),
                estado=EstadoPedidoChoices.PENDIENTE,
                direccion_envio=direccion_envio
            )
            for item in carrito.productos.select_related('producto').all():
                # Si el producto tiene personalización, úsala. Si no, guarda la imagen de catálogo
                if item.personalizacion:
                    personalizacion = item.personalizacion
                elif hasattr(item.producto, 'imagen_referencia') and item.producto.imagen_referencia:
                    personalizacion = {
                        'imagen': item.producto.imagen_referencia.url,
                        'producto_id': item.producto.id,
                        'nombre_producto': item.producto.nombre
                    }
                else:
                    personalizacion = None
                PedidoProducto.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_total=item.subtotal,
                    personalizacion=personalizacion
                )
                if item.producto.stock is not None:
                    item.producto.stock -= item.cantidad
                    item.producto.save()
            pedido.calcular_total()
            carrito.estado = 'finalizado'
            carrito.save()
            
            # Enviar correo con voucher
            from apps.pedidos.emails import enviar_voucher_pedido
            enviar_voucher_pedido(pedido)
        
        messages.success(request, f'Compra de carrito realizada. Pedido #{pedido.numero_pedido}')
        return redirect('pedidos:detalle_pedido', numero_pedido=pedido.numero_pedido)
    except Exception as e:
        logger.error(f"Error al comprar carrito: {str(e)}")
        messages.error(request, 'Error al procesar la compra')
        return redirect('core:home')
@login_required
@require_http_methods(["POST"])
def comprar_subasta(request, subasta_id):
    """
    Compra del ganador de una subasta
    """
    from apps.subastas.models import Subasta, Puja
    try:
        subasta = get_object_or_404(Subasta, id=subasta_id, estado='finalizada')
        puja_ganadora = subasta.pujas.order_by('-monto').first()
        if not puja_ganadora or puja_ganadora.usuario != request.user:
            return HttpResponseBadRequest('No eres el ganador de la subasta.')
        if Pedido.objects.filter(
            usuario=request.user,
            productos__producto=subasta.producto
        ).exists():
            return HttpResponseBadRequest('Ya existe un pedido para esta subasta.')
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                fecha_pedido=timezone.now(),
                estado=EstadoPedidoChoices.PENDIENTE,
                direccion_envio=request.POST.get('direccion_envio', '').strip()
            )
            PedidoProducto.objects.create(
                pedido=pedido,
                producto=subasta.producto,
                cantidad=1,
                precio_total=puja_ganadora.monto
            )
            pedido.calcular_total()
            
            # Enviar correo con voucher
            from apps.pedidos.emails import enviar_voucher_pedido
            enviar_voucher_pedido(pedido)
        
        messages.success(request, f'Compra de subasta realizada. Pedido #{pedido.numero_pedido}')
        return redirect('pedidos:detalle_pedido', numero_pedido=pedido.numero_pedido)
    except Exception as e:
        logger.error(f"Error al comprar subasta: {str(e)}")
        messages.error(request, 'Error al procesar la compra')
        return redirect('subastas:detalle', subasta_id=subasta_id)
@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('productos__producto').order_by('-fecha_pedido')
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})
@login_required
def detalle_pedido(request, numero_pedido):
    pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido, usuario=request.user)
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido})
def es_staff(user):
    """Verificar que el usuario sea staff"""
    return user.is_staff

@login_required
@user_passes_test(es_staff)
@require_http_methods(["POST"]) 
def eliminar_pedido(request, pedido_id):
    """Eliminar un pedido (solo staff)."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    numero = pedido.numero_pedido
    try:
        pedido.delete()
        messages.success(request, f"Pedido {numero} eliminado correctamente.")
    except Exception as e:
        logger.error(f"Error eliminando pedido {numero}: {str(e)}")
        messages.error(request, "No se pudo eliminar el pedido.")
    return redirect('pedidos:panel_pedidos')

@login_required
@user_passes_test(es_staff)
@require_http_methods(["POST"]) 
def acciones_masivas_pedidos(request):
    """Procesa acciones masivas sobre pedidos seleccionados (eliminar, cambiar estado)."""
    accion = request.POST.get('accion')
    # Aceptar tanto nombre 'pedidos' como 'pedidos[]' desde el formulario
    ids = request.POST.getlist('pedidos') or request.POST.getlist('pedidos[]')
    if not ids:
        messages.warning(request, 'No seleccionaste pedidos para la acción masiva.')
        return redirect('pedidos:panel_pedidos')

    pedidos = Pedido.objects.filter(id__in=ids)
    total = pedidos.count()
    if total == 0:
        messages.warning(request, 'No se encontraron pedidos válidos para procesar.')
        return redirect('pedidos:panel_pedidos')

    if accion == 'eliminar':
        numeros = list(pedidos.values_list('numero_pedido', flat=True))
        try:
            pedidos.delete()
            messages.success(request, f"Se eliminaron {len(numeros)} pedidos: {', '.join(numeros[:5])}{'…' if len(numeros) > 5 else ''}")
        except Exception as e:
            logger.error(f"Error en eliminación masiva: {str(e)}")
            messages.error(request, 'Ocurrió un error al eliminar los pedidos')
        actualizados = 0
        for pedido in pedidos:
            estado_anterior = pedido.estado
            # Actualizar fechas específicas según el estado
            if nuevo_estado == 'confirmado' and not pedido.fecha_confirmacion:
                pedido.fecha_confirmacion = timezone.now()
            elif nuevo_estado == 'enviado' and not pedido.fecha_envio:
                pedido.fecha_envio = timezone.now()
                if numero_seguimiento:
                    pedido.numero_seguimiento = numero_seguimiento

            pedido.estado = nuevo_estado
            pedido.save()

            # Registrar en historial
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                usuario_cambio=request.user,
                comentarios=f'Actualización masiva desde panel (antes: {estado_anterior})'
            )

            # Enviar correo según el estado
            try:
                if nuevo_estado == 'confirmado':
                    enviar_confirmacion_pedido(pedido)
                elif nuevo_estado == 'enviado':
                    enviar_notificacion_envio(pedido)
            except Exception as e:
                logger.warning(f"No se pudo enviar notificación para pedido {pedido.id}: {str(e)}")

            actualizados += 1

        messages.success(request, f"Estado actualizado a '{nuevo_estado}' en {actualizados} pedidos.")
        return redirect('pedidos:panel_pedidos')

    messages.error(request, 'Acción masiva no reconocida.')
    return redirect('pedidos:panel_pedidos')

@login_required
@user_passes_test(es_staff)
def panel_pedidos(request):
    """
    Panel principal de administración de pedidos con lista completa
    """
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    busqueda = request.GET.get('busqueda', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Query base con optimización
    pedidos = Pedido.objects.select_related('usuario').prefetch_related('productos__producto').order_by('-fecha_pedido')
    
    # Aplicar filtros
    if estado_filtro:
        pedidos = pedidos.filter(estado=estado_filtro)
    
    if busqueda:
        pedidos = pedidos.filter(
            Q(numero_pedido__icontains=busqueda) |
            Q(usuario__email__icontains=busqueda) |
            Q(usuario__first_name__icontains=busqueda) |
            Q(usuario__last_name__icontains=busqueda)
        )
    
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            pedidos = pedidos.filter(fecha_pedido__gte=fecha_desde_dt)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            pedidos = pedidos.filter(fecha_pedido__lte=fecha_hasta_dt)
        except ValueError:
            pass
    
    # Estadísticas generales
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_confirmados = Pedido.objects.filter(estado='confirmado').count()
    pedidos_enviados = Pedido.objects.filter(estado='enviado').count()
    
    # Ingresos del mes
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = Pedido.objects.filter(
        fecha_pedido__gte=inicio_mes,
        estado__in=['confirmado', 'enviado', 'entregado']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'pedidos': pedidos,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_confirmados': pedidos_confirmados,
        'pedidos_enviados': pedidos_enviados,
        'ingresos_mes': ingresos_mes,
        'estados': EstadoPedidoChoices.choices,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    return render(request, 'pedidos/panel_pedidos.html', context)

# Si api_estadisticas_pedidos debe existir, dejarlo como placeholder:
@login_required
@user_passes_test(es_staff)
def api_estadisticas_pedidos(request):
    # Implementar lógica de estadísticas si es necesario
    return JsonResponse({'status': 'ok'})
    
    return render(request, 'pedidos/panel_pedidos.html', context)

@login_required
@user_passes_test(es_staff)
def lista_pedidos(request):
    """
    Lista de todos los pedidos con filtros
    """
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Query base
    pedidos = Pedido.objects.select_related('usuario').order_by('-fecha_pedido')
    
    # Aplicar filtros
    if estado_filtro:
        pedidos = pedidos.filter(estado=estado_filtro)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        pedidos = pedidos.filter(fecha_pedido__gte=fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        pedidos = pedidos.filter(fecha_pedido__lte=fecha_hasta_dt)
    
    if busqueda:
        pedidos = pedidos.filter(
            Q(numero_pedido__icontains=busqueda) |
            Q(usuario__correo__icontains=busqueda) |
            Q(usuario__nombre__icontains=busqueda)
        )
    
    context = {
        'pedidos': pedidos,
        'estados': EstadoPedidoChoices.choices,
        'estado_filtro': estado_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'busqueda': busqueda,
    }
    
    return render(request, 'pedidos/lista_pedidos.html', context)

@login_required
@user_passes_test(es_staff)
def detalle_pedido_admin(request, pedido_id):
    """
    Vista detallada de un pedido específico para administradores
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    productos = PedidoProducto.objects.filter(pedido=pedido).select_related('producto')
    historial = HistorialEstadoPedido.objects.filter(pedido=pedido).order_by('-fecha_cambio')
    
    # Obtener cartas personalizadas asociadas
    productos_personalizados = []
    for item in pedido.productos.all():
        producto_data = {
            'item': item,
            'carta': None,
            'parametros': []
        }
        
        if hasattr(item, 'carta_personalizada') and item.carta_personalizada:
            # Usar relación directa si existe
            producto_data['carta'] = item.carta_personalizada
            producto_data['parametros'] = item.carta_personalizada.cartaparametro_set.all()
        
        productos_personalizados.append(producto_data)
    
    context = {
        'pedido': pedido,
        'productos': productos,
        'productos_personalizados': productos_personalizados,
        'historial': historial,
        'estados': EstadoPedidoChoices.choices,
    }
    
    return render(request, 'pedidos/detalle_pedido_admin.html', context)

@login_required
@user_passes_test(es_staff)
def cambiar_estado_pedido(request, pedido_id):
    """
    Cambiar el estado de un pedido
    """
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado = request.POST.get('nuevo_estado')
        comentarios = request.POST.get('comentarios', '')
        
        if nuevo_estado in [choice[0] for choice in EstadoPedidoChoices.choices]:
            estado_anterior = pedido.estado
            
            # Actualizar fechas específicas según el estado
            if nuevo_estado == 'confirmado' and not pedido.fecha_confirmacion:
                pedido.fecha_confirmacion = timezone.now()
            elif nuevo_estado == 'enviado' and not pedido.fecha_envio:
                pedido.fecha_envio = timezone.now()
                numero_seguimiento = request.POST.get('numero_seguimiento', '')
                if numero_seguimiento:
                    pedido.numero_seguimiento = numero_seguimiento
            
            pedido.estado = nuevo_estado
            pedido.save()
            
            # Registrar en historial
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
                usuario_cambio=request.user,
                comentarios=comentarios
            )
            
            # Enviar correo según el estado
            if nuevo_estado == 'confirmado':
                enviar_confirmacion_pedido(pedido)
            elif nuevo_estado == 'enviado':
                enviar_notificacion_envio(pedido)
            
            messages.success(request, f'Estado del pedido actualizado a: {nuevo_estado}')
        else:
            messages.error(request, 'Estado no válido')
    
    return redirect('pedidos:detalle_pedido_admin', pedido_id=pedido_id)

@login_required
def mis_pedidos(request):
    """
    Vista para que los usuarios vean sus propios pedidos
    """
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'pedidos/mis_pedidos.html', context)

@login_required
def detalle_mi_pedido(request, pedido_id):
    """
    Vista para que el usuario vea el detalle de su propio pedido
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    productos = PedidoProducto.objects.filter(pedido=pedido).select_related('producto')
    
    context = {
        'pedido': pedido,
        'productos': productos,
    }
    
    return render(request, 'pedidos/detalle_mi_pedido.html', context)

@login_required
@user_passes_test(es_staff)
def descargar_pedido_pdf(request, pedido_id):
    """
    Descargar pedido como PDF
    """
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.units import inch
    from io import BytesIO
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Crear buffer
    buffer = BytesIO()
    
    # Crear PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    titulo = Paragraph(f"<b>Pedido #{pedido.numero_pedido}</b>", styles['Title'])
    elements.append(titulo)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del pedido
    info_data = [
        ['Fecha:', pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M')],
        ['Estado:', pedido.get_estado_display()],
        ['Cliente:', f"{pedido.usuario.first_name} {pedido.usuario.last_name}"],
        ['Email:', pedido.usuario.email],
        ['Dirección:', pedido.direccion_envio or 'N/A'],
        ['Total:', f"${pedido.total:,.0f}" if pedido.total else 'N/A'],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Productos
    elements.append(Paragraph("<b>Productos</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))

    # Para cada producto, intentar adjuntar imagen de carta personalizada si existe
    from django.core.exceptions import ObjectDoesNotExist
    try:
        from apps.personalizacion.models import CartaPersonalizada
    except Exception:
        CartaPersonalizada = None

    for item in pedido.productos.all():
        # Construir descripción del producto
        precio_unitario = (item.precio_total / item.cantidad) if item.cantidad else 0
        detalles_html = (
            f"<b>{item.producto.nombre}</b><br/>") + \
            (f"Cantidad: {item.cantidad}<br/>" if item.cantidad else "") + \
            f"Precio unitario: ${precio_unitario:,.0f}<br/>Subtotal: ${item.precio_total:,.0f}"

        # Buscar carta personalizada asociada
        carta = getattr(item, 'carta_personalizada', None)
        if not carta and CartaPersonalizada and getattr(item, 'personalizacion', None):
            personalizacion_data = item.personalizacion
            if isinstance(personalizacion_data, dict) and 'carta_id' in personalizacion_data:
                try:
                    carta = CartaPersonalizada.objects.filter(id=personalizacion_data['carta_id']).first()
                except ObjectDoesNotExist:
                    carta = None

        # Preparar layout: con o sin imagen
        row_flowable = None
        if carta and getattr(carta, 'imagen_frente', None) and carta.imagen_frente:
            try:
                img_path = carta.imagen_frente.path
                img = Image(img_path)
                # Limitar tamaño manteniendo proporción (aprox 2.5x3.5 inches)
                img._restrictSize(2.5*inch, 3.5*inch)

                detalles_paragraph = Paragraph(detalles_html, styles['BodyText'])
                row_flowable = Table(
                    [[img, detalles_paragraph]],
                    colWidths=[2.7*inch, 3.8*inch]
                )
                row_flowable.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
            except Exception:
                # Si no se pudo cargar imagen, caer al bloque sin imagen
                row_flowable = None

        if row_flowable is None:
            detalles_paragraph = Paragraph(detalles_html, styles['BodyText'])
            row_flowable = Table(
                [[detalles_paragraph]],
                colWidths=[6.5*inch]
            )
            row_flowable.setStyle(TableStyle([
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))

        # Marco alrededor de cada producto
        wrapper = Table(
            [[row_flowable]],
            colWidths=[6.5*inch]
        )
        wrapper.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ]))

        elements.append(wrapper)
        elements.append(Spacer(1, 0.2*inch))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener PDF del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pedido_{pedido.numero_pedido}.pdf"'
    response.write(pdf)
    
    return response

@login_required
@user_passes_test(es_staff)
def enviar_mensaje_cliente(request, pedido_id):
    """
    Enviar mensaje al cliente por email
    """
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        asunto = request.POST.get('asunto', '')
        mensaje = request.POST.get('mensaje', '')
        
        if asunto and mensaje:
            from django.core.mail import send_mail
            
            try:
                send_mail(
                    subject=f"[NM Collections] {asunto} - Pedido #{pedido.numero_pedido}",
                    message=mensaje,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[pedido.usuario.email],
                    fail_silently=False,
                )
                messages.success(request, 'Mensaje enviado exitosamente al cliente')
            except Exception as e:
                logger.error(f"Error al enviar mensaje: {str(e)}")
                messages.error(request, 'Error al enviar el mensaje')
        else:
            messages.error(request, 'Debe completar el asunto y mensaje')
    
    return redirect('pedidos:detalle_pedido_admin', pedido_id=pedido_id)

# API endpoints para estadísticas
@login_required
@user_passes_test(es_staff)
def api_estadisticas_pedidos(request):
    """
    API para obtener estadísticas de pedidos (para gráficos)
    """
    # Estadísticas por día de los últimos 30 días
    hace_30_dias = timezone.now() - timedelta(days=30)
    
    estadisticas = Pedido.objects.filter(
        fecha_pedido__gte=hace_30_dias
    ).extra(
        select={'fecha': 'date(fecha_pedido)'}
    ).values('fecha').annotate(
        count=Count('id'),
        total_ingresos=Sum('total')
    ).order_by('fecha')
    
    return JsonResponse({
        'estadisticas_diarias': list(estadisticas),
        'resumen': {
            'total_pedidos_30d': Pedido.objects.filter(fecha_pedido__gte=hace_30_dias).count(),
            'ingresos_30d': Pedido.objects.filter(
                fecha_pedido__gte=hace_30_dias,
                estado__in=['confirmado', 'enviado', 'entregado']
            ).aggregate(total=Sum('total'))['total'] or 0
        }
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.contrib import messages

from apps.pedidos.models import Pedido, PedidoProducto, HistorialEstadoPedido
from apps.carrito.models import Carrito
from apps.productos.models import Producto
from apps.core.models import EstadoPedidoChoices
from apps.pedidos.emails import enviar_voucher_pedido, enviar_confirmacion_pedido, enviar_notificacion_envio

from apps.pagos.views import iniciar_pago_webpay

import logging

logger = logging.getLogger(__name__)


def crear_carta_view(request):
    """Vista legacy - mantener por compatibilidad"""
    return render(request, 'crearcarta/menu-crear.html')


@login_required
def detalle_pedido_usuario(request, pedido_id):
    """Vista para que un usuario vea el detalle de su propio pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Obtener historial de estados
    historial = HistorialEstadoPedido.objects.filter(pedido=pedido).order_by('-fecha_cambio')
    
    # Obtener cartas personalizadas asociadas directamente
    productos_personalizados = []
    for item in pedido.productos.all():
        if hasattr(item, 'carta_personalizada') and item.carta_personalizada:
            # Usar relación directa si existe
            productos_personalizados.append({
                'item': item,
                'carta': item.carta_personalizada,
                'parametros': item.carta_personalizada.cartaparametro_set.all()
            })
        elif hasattr(item, 'personalizacion') and item.personalizacion:
            # Fallback: buscar por datos de personalización
            personalizacion_data = item.personalizacion
            if isinstance(personalizacion_data, dict) and 'carta_id' in personalizacion_data:
                try:
                    from apps.personalizacion.models import CartaPersonalizada
                    carta = CartaPersonalizada.objects.get(
                        id=personalizacion_data['carta_id'], 
                        usuario=request.user
                    )
                    productos_personalizados.append({
                        'item': item,
                        'carta': carta,
                        'parametros': carta.cartaparametro_set.all()
                    })
                except CartaPersonalizada.DoesNotExist:
                    pass
    
    context = {
        'pedido': pedido,
        'historial': historial,
        'productos_personalizados': productos_personalizados,
    }
    
    return render(request, 'pedidos/detalle_pedido_usuario.html', context)


@login_required
def cancelar_pedido_usuario(request, pedido_id):
    """Vista para que un usuario cancele su propio pedido (solo si está pendiente)"""
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
        
        if pedido.estado == 'pendiente':
            # Cambiar estado a cancelado
            pedido.estado = 'cancelado'
            pedido.fecha_actualizacion = timezone.now()
            pedido.save()
            
            # Registrar en historial
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior='pendiente',
                estado_nuevo='cancelado',
                comentarios='Cancelado por el cliente'
            )
            
            messages.success(request, f'Pedido #{pedido.id} cancelado exitosamente.')
        else:
            messages.error(request, 'Solo se pueden cancelar pedidos en estado pendiente.')
    
    return redirect('pedidos:mis_pedidos')


@login_required
def confirmar_entrega_usuario(request, pedido_id):
    """
    Permitir al usuario confirmar que recibió su pedido
    """
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
        
        # Solo permitir confirmar entrega si el pedido está en estado 'enviado'
        if pedido.estado == 'enviado':
            estado_anterior = pedido.estado
            pedido.estado = 'entregado'
            # pedido.fecha_entrega = timezone.now()  # Campo no existe en el modelo
            pedido.save()
            
            # Registrar en historial
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior=estado_anterior,
                estado_nuevo='entregado',
                comentarios='Entrega confirmada por el cliente',
                usuario_cambio=request.user
            )
            
            messages.success(request, f'¡Gracias! Has confirmado la entrega del pedido #{pedido.id}.')
        else:
            messages.error(request, 'Solo se puede confirmar la entrega de pedidos que están en estado "Enviado".')
    
    return redirect('pedidos:detalle_pedido_usuario', pedido_id=pedido_id)
@require_http_methods(["POST"])
def comprar_producto(request, producto_id):
    """
    Compra directa de un producto desde el catálogo
    """
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        direccion_envio = request.POST.get('direccion_envio', '').strip()
        
        # Validar dirección
        if not direccion_envio:
            messages.error(request, 'Debe ingresar una dirección de envío')
            return redirect('productos:detalle', producto_id=producto_id)
        
        # Validar stock
        if producto.stock is not None and producto.stock < cantidad:
            messages.error(request, f'Stock insuficiente. Disponible: {producto.stock}')
            return redirect('productos:detalle', producto_id=producto_id)
        
        with transaction.atomic():
            # Crear pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                metodo_pago='webpay',
                direccion_envio=direccion_envio,
                estado=EstadoPedidoChoices.PENDIENTE
            )
            
            # Agregar producto al pedido
            precio_total = producto.precio_base * cantidad
            PedidoProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_total=precio_total
            )
            
            # Reducir stock
            if producto.stock is not None:
                producto.stock -= cantidad
                producto.save()
            
            # Calcular total
            pedido.calcular_total()
            
            # Crear historial
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior=None,
                estado_nuevo=EstadoPedidoChoices.PENDIENTE,
                usuario_cambio=request.user,
                comentarios='Pedido creado - Compra directa'
            )
            
            # Iniciar pago con WebPay
            webpay_data = iniciar_pago_webpay(pedido)
            
            if webpay_data:
                # Redirigir a WebPay
                return render(request, 'pagos/redirect_webpay.html', {
                    'payment_url': webpay_data['url'],
                    'payment_token': webpay_data['token']
                })
            else:
                messages.error(request, 'Error al iniciar el pago')
                return redirect('productos:detalle', producto_id=producto_id)
    
    except Exception as e:
        logger.error(f"Error al comprar producto: {str(e)}")
        messages.error(request, 'Error al procesar la compra')
        return redirect('productos:detalle', producto_id=producto_id)


@login_required
@require_http_methods(["POST"])
def comprar_carrito(request):
    """
    Compra todos los productos del carrito
    """
    try:
        carrito = Carrito.objects.filter(usuario=request.user, estado='activo').first()
        
        if not carrito or not carrito.productos.exists():
            messages.error(request, 'No tienes productos en el carrito')
            return redirect('core:home')
        
        direccion_envio = request.POST.get('direccion_envio', '').strip()
        
        if not direccion_envio:
            messages.error(request, 'Debe ingresar una dirección de envío')
            return redirect('core:home')  # O donde tengas el carrito
        
        with transaction.atomic():
            # Crear pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                metodo_pago='webpay',
                direccion_envio=direccion_envio,
                estado=EstadoPedidoChoices.PENDIENTE
            )
            
            # Transferir productos del carrito al pedido
            for item in carrito.productos.all():
                # Validar stock
                if item.producto.stock is not None and item.producto.stock < item.cantidad:
                    messages.error(request, f'Stock insuficiente para {item.producto.nombre}')
                    pedido.delete()
                    return redirect('core:home')
                
                PedidoProducto.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    personalizacion=item.personalizacion,
                    precio_total=item.subtotal
                )
                
                # Reducir stock
                if item.producto.stock is not None:
                    item.producto.stock -= item.cantidad
                    item.producto.save()
            
            # Calcular total
            pedido.calcular_total()
            
            # Limpiar carrito
            carrito.productos.all().delete()
            carrito.estado = 'finalizado'
            carrito.save()
            
            # Crear historial
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior=None,
                estado_nuevo=EstadoPedidoChoices.PENDIENTE,
                usuario_cambio=request.user,
                comentarios='Pedido creado desde carrito'
            )
            
            # Iniciar pago con WebPay
            webpay_data = iniciar_pago_webpay(pedido)
            
            if webpay_data:
                return render(request, 'pagos/redirect_webpay.html', {
                    'payment_url': webpay_data['url'],
                    'payment_token': webpay_data['token']
                })
            else:
                messages.error(request, 'Error al iniciar el pago')
                return redirect('core:home')
    
    except Exception as e:
        logger.error(f"Error al comprar carrito: {str(e)}")
        messages.error(request, 'Error al procesar la compra')
        return redirect('core:home')


@login_required
@require_http_methods(["POST"])
def comprar_subasta(request, subasta_id):
    """
    Compra del ganador de una subasta
    """
    from apps.subastas.models import Subasta, Puja
    
    try:
        subasta = get_object_or_404(Subasta, id=subasta_id, estado='finalizada')
        
        # Verificar que el usuario sea el ganador
        puja_ganadora = subasta.pujas.order_by('-monto').first()
        
        if not puja_ganadora or puja_ganadora.usuario != request.user:
            messages.error(request, 'No eres el ganador de esta subasta')
            return redirect('subastas:detalle', subasta_id=subasta_id)
        
        # Verificar si ya existe un pedido para esta subasta
        if Pedido.objects.filter(
            usuario=request.user,
            productos__producto=subasta.producto
        ).exists():
            messages.info(request, 'Ya has realizado un pedido para esta subasta')
            return redirect('usuarios:dashboard')
        
        direccion_envio = request.POST.get('direccion_envio', '').strip()
        
        if not direccion_envio:
            messages.error(request, 'Debe ingresar una dirección de envío')
            return redirect('subastas:detalle', subasta_id=subasta_id)
        
        with transaction.atomic():
            # Crear pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                metodo_pago='webpay',
                direccion_envio=direccion_envio,
                notas=f'Subasta ID: {subasta.id}',
                estado=EstadoPedidoChoices.PENDIENTE
            )
            
            # Agregar producto con precio de la puja ganadora
            PedidoProducto.objects.create(
                pedido=pedido,
                producto=subasta.producto,
                cantidad=1,
                precio_total=puja_ganadora.monto
            )
            
            # Reducir stock
            if subasta.producto.stock is not None:
                subasta.producto.stock -= 1
                subasta.producto.save()
            
            # Calcular total
            pedido.calcular_total()
            
            # Crear historial
            HistorialEstadoPedido.objects.create(
                pedido=pedido,
                estado_anterior=None,
                estado_nuevo=EstadoPedidoChoices.PENDIENTE,
                usuario_cambio=request.user,
                comentarios=f'Pedido creado - Subasta ganada #{subasta.id}'
            )
            
            # Iniciar pago con WebPay
            webpay_data = iniciar_pago_webpay(pedido)
            
            if webpay_data:
                return render(request, 'pagos/redirect_webpay.html', {
                    'payment_url': webpay_data['url'],
                    'payment_token': webpay_data['token']
                })
            else:
                messages.error(request, 'Error al iniciar el pago')
                return redirect('subastas:detalle', subasta_id=subasta_id)
    
    except Exception as e:
        logger.error(f"Error al comprar subasta: {str(e)}")
        messages.error(request, 'Error al procesar la compra')
        return redirect('subastas:detalle', subasta_id=subasta_id)


@login_required
def mis_pedidos(request):
    """Lista los pedidos del usuario"""
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('productos__producto').order_by('-fecha_pedido')
    
    return render(request, 'pedidos/mis_pedidos.html', {
        'pedidos': pedidos
    })


@login_required
def detalle_pedido(request, numero_pedido):
    """Detalle de un pedido específico (usuario)"""
    pedido = get_object_or_404(
        Pedido,
        numero_pedido=numero_pedido,
        usuario=request.user
    )
    
    return render(request, 'pedidos/detalle_pedido.html', {
        'pedido': pedido
    })
