from apps.personalizacion.models import CartaPersonalizada
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["POST"])

def agregar_carta_personalizada(request, carta_id):
    """
    Agrega una carta personalizada finalizada al carrito como producto único
    """
    try:
        from apps.productos.models import CategoriaProducto, Producto
        carta = get_object_or_404(CartaPersonalizada, id=carta_id, usuario=request.user, estado='finalizada')
        # Buscar si ya existe un producto único para esta carta
        producto_nombre = f"Carta Personalizada #{carta.id} - {carta.nombre_carta or 'Personalizada'}"
        producto_carta = Producto.objects.filter(nombre=producto_nombre, tipo='personalizado').first()
        if not producto_carta:
            # Obtener o crear categoría
            categoria_carta, _ = CategoriaProducto.objects.get_or_create(
                nombre='Carta Personalizada', defaults={'descripcion': 'Cartas personalizadas de trading'}
            )
            # Crear producto único para la carta
            producto_carta = Producto.objects.create(
                nombre=producto_nombre,
                descripcion=f"Carta personalizada basada en plantilla {carta.plantilla.nombre}",
                precio_base=15000,
                categoria=categoria_carta,
                tipo='personalizado',
                estado='activo'
            )
        # Obtener o crear carrito activo
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user, estado='activo')
        # Verificar si el producto ya está en el carrito
        item_carrito, item_created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto_carta,
            defaults={
                'cantidad': 1,
                'precio_unitario': producto_carta.precio_base,
                'personalizacion': {
                    'carta_id': carta.id,
                    'nombre_carta': carta.nombre_carta,
                    'imagen': carta.imagen_generada.url if carta.imagen_generada else '',
                    'parametros': [
                        {
                            'nombre': param.nombre_parametro,
                            'valor': param.valor
                        } for param in carta.cartaparametro_set.all()
                    ]
                }
            }
        )
        if not item_created:
            item_carrito.cantidad += 1
            item_carrito.save()
        messages.success(request, 'Carta personalizada agregada al carrito')
        return redirect('carrito:ver_carrito')
    except Exception as e:
        import logging
        logging.error(f"Error al agregar carta personalizada al carrito: {str(e)}")
        messages.error(request, 'Error al agregar la carta personalizada al carrito')
        return redirect('personalizacion:mis_cartas')
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Sum, F

from apps.carrito.models import Carrito, CarritoProducto
from apps.productos.models import Producto

import logging

logger = logging.getLogger(__name__)


@login_required
def ver_carrito(request):
    """Vista principal del carrito de compras"""
    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        estado='activo'
    )
    
    items = carrito.productos.select_related('producto').all()
    
    # Calcular totales
    subtotal = sum(item.subtotal for item in items)
    total_items = sum(item.cantidad for item in items)
    
    context = {
        'carrito': carrito,
        'items': items,
        'subtotal': subtotal,
        'total_items': total_items,
        'total': subtotal,  # Aquí podrías agregar costos de envío, descuentos, etc.
    }
    
    return render(request, 'carrito/ver_carrito.html', context)


@login_required
@require_http_methods(["POST"])
def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito"""
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Validar cantidad
        if cantidad <= 0:
            messages.error(request, 'La cantidad debe ser mayor a 0')
            return redirect('productos:detalle', producto_id=producto_id)
        
        # Validar stock
        if producto.stock is not None and producto.stock < cantidad:
            messages.error(request, f'Stock insuficiente. Disponible: {producto.stock}')
            return redirect('productos:detalle', producto_id=producto_id)
        
        # Obtener o crear carrito activo
        carrito, created = Carrito.objects.get_or_create(
            usuario=request.user,
            estado='activo'
        )
        
        # Verificar si el producto ya está en el carrito
        personalizacion = None
        if producto.imagen_referencia:
            personalizacion = {
                'imagen': producto.imagen_referencia.url,
                'producto_id': producto.id,
                'nombre_producto': producto.nombre
            }
        item_carrito, item_created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={
                'cantidad': cantidad,
                'precio_unitario': producto.precio_base,
                'personalizacion': personalizacion
            }
        )
        
        if not item_created:
            # Si ya existe, actualizar cantidad
            nueva_cantidad = item_carrito.cantidad + cantidad
            
            # Validar stock total
            if producto.stock is not None and producto.stock < nueva_cantidad:
                messages.error(request, f'No hay suficiente stock. Máximo disponible: {producto.stock}')
                return redirect('productos:detalle', producto_id=producto_id)
            
            item_carrito.cantidad = nueva_cantidad
            item_carrito.save()
            messages.success(request, f'Se actualizó la cantidad de {producto.nombre} en el carrito')
        else:
            messages.success(request, f'{producto.nombre} agregado al carrito')
        
        # Redirigir según parámetro
        next_url = request.POST.get('next', 'carrito:ver_carrito')
        return redirect(next_url)
        
    except Exception as e:
        logger.error(f"Error al agregar producto al carrito: {str(e)}")
        messages.error(request, 'Error al agregar el producto al carrito')
        return redirect('productos:detalle', producto_id=producto_id)


@login_required
@require_http_methods(["POST"])
def actualizar_cantidad(request, item_id):
    """Actualiza la cantidad de un item en el carrito"""
    try:
        item = get_object_or_404(
            CarritoProducto,
            id=item_id,
            carrito__usuario=request.user,
            carrito__estado='activo'
        )
        
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad <= 0:
            # Si la cantidad es 0 o negativa, eliminar el item
            item.delete()
            messages.success(request, f'{item.producto.nombre} eliminado del carrito')
        else:
            # Validar stock
            if item.producto.stock is not None and item.producto.stock < cantidad:
                messages.error(request, f'Stock insuficiente. Disponible: {item.producto.stock}')
                return redirect('carrito:ver_carrito')
            
            item.cantidad = cantidad
            item.save()
        
        return redirect('carrito:ver_carrito')
        
    except Exception as e:
        logger.error(f"Error al actualizar cantidad: {str(e)}")
        messages.error(request, 'Error al actualizar la cantidad')
        return redirect('carrito:ver_carrito')


@login_required
@require_http_methods(["POST"])
def eliminar_del_carrito(request, item_id):
    """Elimina un producto del carrito"""
    try:
        item = get_object_or_404(
            CarritoProducto,
            id=item_id,
            carrito__usuario=request.user,
            carrito__estado='activo'
        )
        
        producto_nombre = item.producto.nombre
        item.delete()
        
        messages.success(request, f'{producto_nombre} eliminado del carrito')
        return redirect('carrito:ver_carrito')
        
    except Exception as e:
        logger.error(f"Error al eliminar del carrito: {str(e)}")
        messages.error(request, 'Error al eliminar el producto')
        return redirect('carrito:ver_carrito')



@login_required
@require_http_methods(["POST"])
def vaciar_carrito(request):
    """Vacía completamente el carrito"""
    try:
        carrito = Carrito.objects.filter(
            usuario=request.user,
            estado='activo'
        ).first()
        
        if carrito:
            carrito.productos.all().delete()
            messages.success(request, 'Carrito vaciado correctamente')
        
        return redirect('carrito:ver_carrito')
        
    except Exception as e:
        logger.error(f"Error al vaciar carrito: {str(e)}")
        messages.error(request, 'Error al vaciar el carrito')
        return redirect('carrito:ver_carrito')


@login_required
def obtener_cantidad_carrito(request):
    """Retorna la cantidad de items en el carrito (para actualizar badge)"""
    try:
        carrito = Carrito.objects.filter(
            usuario=request.user,
            estado='activo'
        ).first()
        
        if carrito:
            total_items = carrito.productos.aggregate(
                total=Sum('cantidad')
            )['total'] or 0
        else:
            total_items = 0
        
        return JsonResponse({'total_items': total_items})
        
    except Exception as e:
        logger.error(f"Error al obtener cantidad: {str(e)}")
        return JsonResponse({'total_items': 0})
