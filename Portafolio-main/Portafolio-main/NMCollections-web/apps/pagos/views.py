from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.contrib import messages

from apps.pedidos.models import Pedido, HistorialEstadoPedido
from apps.core.models import EstadoPedidoChoices
from apps.pagos.models import TransaccionPago

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType

import logging
import random

logger = logging.getLogger(__name__)


def obtener_info_tipo_pago(response):
    """
    Extrae información del tipo de pago desde la respuesta de WebPay
    Retorna diccionario con tipo, código y descripción
    """
    payment_type_code = response.get('payment_type_code', '')
    
    # Mapeo de códigos de pago
    tipos_pago = {
        'VD': {
            'tipo': 'WebPay Débito',
            'categoria': 'debito',
            'descripcion': 'Débito Bancario'
        },
        'VN': {
            'tipo': 'WebPay Crédito',
            'categoria': 'credito',
            'descripcion': 'Crédito en 1 cuota'
        },
        'VC': {
            'tipo': 'WebPay Crédito',
            'categoria': 'credito',
            'descripcion': 'Crédito en cuotas normales'
        },
        'SI': {
            'tipo': 'WebPay Crédito',
            'categoria': 'credito',
            'descripcion': 'Crédito 3 cuotas sin interés'
        },
        'S2': {
            'tipo': 'WebPay Crédito',
            'categoria': 'credito',
            'descripcion': 'Crédito 2 cuotas sin interés'
        },
        'NC': {
            'tipo': 'WebPay Crédito',
            'categoria': 'credito',
            'descripcion': 'Crédito N cuotas sin interés'
        },
        'VP': {
            'tipo': 'WebPay Prepago',
            'categoria': 'prepago',
            'descripcion': 'Venta Prepago'
        }
    }
    
    info = tipos_pago.get(payment_type_code, {
        'tipo': 'WebPay',
        'categoria': 'otro',
        'descripcion': 'Pago WebPay'
    })
    
    # Agregar información adicional de la respuesta
    info['codigo'] = payment_type_code
    info['cuotas'] = response.get('installments_number', 0)
    info['ultimos_4_digitos'] = response.get('card_detail', {}).get('card_number', '')[-4:] if response.get('card_detail') else ''
    
    return info


def get_webpay_transaction():
    """Obtiene instancia de Transaction configurada"""
    if settings.WEBPAY_ENVIRONMENT == 'TEST':
        # Usar credenciales de integración (testing)
        return Transaction(WebpayOptions(
            commerce_code=settings.WEBPAY_COMMERCE_CODE,
            api_key=settings.WEBPAY_API_KEY,
            integration_type=IntegrationType.TEST
        ))
    else:
        # Usar credenciales de producción
        return Transaction(WebpayOptions(
            commerce_code=settings.WEBPAY_COMMERCE_CODE,
            api_key=settings.WEBPAY_API_KEY,
            integration_type=IntegrationType.LIVE
        ))


def iniciar_pago_webpay(pedido):
    """
    Inicia el proceso de pago con Transbank WebPay Plus
    Retorna la URL de pago y el token o None si hay error
    """
    try:
        tx = get_webpay_transaction()
        
        # Generar order_id único
        buy_order = f"{pedido.numero_pedido}-{random.randint(1000, 9999)}"
        session_id = str(pedido.usuario.id)
        amount = int(pedido.total)  # Monto en pesos chilenos (entero)
        
        # URL de retorno
        return_url = f"{settings.SITE_URL}/pagos/webpay/retorno/"
        
        # Crear transacción
        response = tx.create(buy_order, session_id, amount, return_url)
        
        # Crear registro de transacción
        transaccion = TransaccionPago.objects.create(
            pedido=pedido,
            monto=pedido.total,
            metodo_pago='webpay',
            gateway_transaction_id=response['token'],
            detalle_response=response
        )
        
        # Guardar token en el pedido
        pedido.notas = f"{pedido.notas}\nWebPay Token: {response['token']}"
        pedido.save()
        
        logger.info(f"WebPay creado para pedido {pedido.numero_pedido}: {response['token']}")
        
        return {
            'url': response['url'],
            'token': response['token']
        }
    
    except Exception as e:
        logger.error(f"Error al iniciar pago con WebPay: {str(e)}")
        return None


@csrf_exempt
@require_http_methods(["POST", "GET"])
def webpay_retorno(request):
    """
    Procesa el retorno de WebPay Plus
    Esta vista recibe al usuario después de completar el pago
    """
    try:
        # Obtener token desde POST o GET
        token = request.POST.get('token_ws') or request.GET.get('token_ws')
        
        if not token:
            messages.error(request, 'Token de pago inválido')
            return redirect('pagos:pago_failure')
        
        # Confirmar transacción
        tx = get_webpay_transaction()
        response = tx.commit(token)
        
        logger.info(f"WebPay response: {response}")
        
        # Extraer numero de pedido del buy_order
        # buy_order fue generado como f"{pedido.numero_pedido}-{random}"
        # donde numero_pedido ya contiene un guión (e.g., "PED-ABC12345").
        # Por lo tanto, debemos eliminar solo el sufijo aleatorio usando rsplit.
        buy_order = response['buy_order']
        numero_pedido = buy_order.rsplit('-', 1)[0]
        
        # Buscar pedido
        try:
            pedido = Pedido.objects.get(numero_pedido=numero_pedido)
            
            # Buscar transacción
            transaccion = TransaccionPago.objects.filter(
                pedido=pedido,
                gateway_transaction_id=token
            ).first()
            
            estado_anterior = pedido.estado
            
            # Obtener información detallada del tipo de pago
            info_pago = obtener_info_tipo_pago(response)
            tipo_pago = info_pago['tipo']
            
            # Actualizar método de pago en el pedido
            pedido.metodo_pago = tipo_pago
            
            # Verificar estado de la transacción
            if response['response_code'] == 0 and response['status'] == 'AUTHORIZED':
                # Pago exitoso
                pedido.estado = EstadoPedidoChoices.CONFIRMADO
                pedido.fecha_confirmacion = timezone.now()
                pedido.notas = f"{pedido.notas}\nWebPay Auth Code: {response['authorization_code']}"
                pedido.save()
                
                # Actualizar transacción
                if transaccion:
                    transaccion.marcar_como_aprobada(codigo_autorizacion=response['authorization_code'])
                    transaccion.gateway_response_code = str(response['response_code'])
                    transaccion.metodo_pago = tipo_pago
                    transaccion.detalle_response = response
                    transaccion.save()
                
                # Registrar cambio de estado
                HistorialEstadoPedido.objects.create(
                    pedido=pedido,
                    estado_anterior=estado_anterior,
                    estado_nuevo=pedido.estado,
                    comentarios=f'Pago confirmado con {tipo_pago}. Auth: {response["authorization_code"]}'
                )
                
                # Enviar correo con voucher
                from apps.pedidos.emails import enviar_voucher_pedido
                print(f"\n[DEBUG] Pago exitoso, enviando voucher para pedido #{numero_pedido}")
                enviar_voucher_pedido(pedido)
                
                logger.info(f"Pedido {numero_pedido} confirmado con WebPay")
                
                # Guardar info en sesión para mostrar en página de éxito
                request.session['pedido_exitoso'] = {
                    'numero_pedido': numero_pedido,
                    'total': str(pedido.total),
                    'auth_code': response['authorization_code'],
                    'tipo_pago': tipo_pago,
                    'cuotas': info_pago['cuotas'],
                    'ultimos_4_digitos': info_pago['ultimos_4_digitos']
                }
                
                return redirect('pagos:pago_success')
            
            else:
                # Pago rechazado o fallido
                pedido.estado = EstadoPedidoChoices.CANCELADO
                
                # Devolver stock
                for item in pedido.productos.all():
                    if item.producto.stock is not None:
                        item.producto.stock += item.cantidad
                        item.producto.save()
                
                # Actualizar transacción
                if transaccion:
                    transaccion.marcar_como_fallida(razon=f"Código de respuesta: {response['response_code']}")
                    transaccion.gateway_response_code = str(response['response_code'])
                    transaccion.gateway_response_message = response.get('status', '')
                    transaccion.metodo_pago = tipo_pago
                    transaccion.detalle_response = response
                    transaccion.save()
                
                # Registrar cambio de estado
                HistorialEstadoPedido.objects.create(
                    pedido=pedido,
                    estado_anterior=estado_anterior,
                    estado_nuevo=pedido.estado,
                    comentarios=f'Pago rechazado por WebPay. Código: {response["response_code"]}'
                )
                
                pedido.save()
                logger.warning(f"Pedido {numero_pedido} rechazado. Código: {response['response_code']}")
                
                messages.error(request, 'El pago fue rechazado')
                return redirect('pagos:pago_failure')
        
        except Pedido.DoesNotExist:
            logger.error(f"Pedido {numero_pedido} no encontrado en retorno WebPay")
            messages.error(request, 'Pedido no encontrado')
            return redirect('pagos:pago_failure')
    
    except Exception as e:
        logger.error(f"Error en retorno de WebPay: {str(e)}")
        messages.error(request, 'Error al procesar el pago')
        return redirect('pagos:pago_failure')


@login_required
def pago_success(request):
    """Página de pago exitoso"""
    pedido_info = request.session.get('pedido_exitoso', {})
    
    # Limpiar sesión
    if 'pedido_exitoso' in request.session:
        del request.session['pedido_exitoso']
    
    return render(request, 'pagos/pago_success.html', {
        'pedido_info': pedido_info
    })


@login_required
def pago_failure(request):
    """Página de pago fallido"""
    return render(request, 'pagos/pago_failure.html')
