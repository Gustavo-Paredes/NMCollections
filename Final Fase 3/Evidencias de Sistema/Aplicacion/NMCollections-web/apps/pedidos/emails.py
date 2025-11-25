"""
Módulo para envío de correos electrónicos relacionados con pedidos
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def enviar_voucher_pedido(pedido):
    """
    Envía el voucher de compra al correo del usuario
    
    Args:
        pedido: Instancia del modelo Pedido
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        print(f"\n{'='*60}")
        print(f"[DEBUG] Iniciando envío de voucher")
        print(f"[DEBUG] Pedido: #{pedido.numero_pedido}")
        print(f"[DEBUG] Usuario: {pedido.usuario.username}")
        print(f"[DEBUG] Email destino: {pedido.usuario.email}")
        
        # Contexto para el template
        context = {
            'pedido': pedido,
            'usuario': pedido.usuario,
            'productos': pedido.productos.all(),
            'site_url': settings.SITE_URL,
        }
        
        print(f"[DEBUG] Contexto preparado con {pedido.productos.count()} productos")
        
        # Renderizar template HTML
        html_content = render_to_string('emails/voucher_pedido.html', context)
        text_content = strip_tags(html_content)  # Versión texto plano
        
        print(f"[DEBUG] Template renderizado correctamente")
        
        # Crear email
        subject = f'Voucher de Compra - Pedido #{pedido.numero_pedido}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = pedido.usuario.email
        
        print(f"[DEBUG] From: {from_email}")
        print(f"[DEBUG] To: {to_email}")
        print(f"[DEBUG] Subject: {subject}")
        print(f"[DEBUG] Email HOST: {settings.EMAIL_HOST}")
        print(f"[DEBUG] Email PORT: {settings.EMAIL_PORT}")
        print(f"[DEBUG] Email USER: {settings.EMAIL_HOST_USER}")
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        
        # Adjuntar versión HTML
        email.attach_alternative(html_content, "text/html")
        
        print(f"[DEBUG] Email preparado, enviando...")
        
        # Enviar
        email.send()
        
        print(f"[DEBUG] ✓ Email enviado exitosamente")
        print(f"{'='*60}\n")
        
        logger.info(f"Voucher enviado a {to_email} para pedido #{pedido.numero_pedido}")
        return True
        
    except Exception as e:
        print(f"[ERROR] ✗ Falló el envío del email")
        print(f"[ERROR] Tipo de error: {type(e).__name__}")
        print(f"[ERROR] Mensaje: {str(e)}")
        print(f"{'='*60}\n")
        logger.error(f"Error al enviar voucher: {str(e)}")
        return False


def enviar_confirmacion_pedido(pedido):
    """
    Envía confirmación cuando el pedido cambia a estado confirmado
    """
    try:
        print(f"\n[DEBUG] Enviando confirmación de pedido #{pedido.numero_pedido} a {pedido.usuario.email}")
        
        context = {
            'pedido': pedido,
            'usuario': pedido.usuario,
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string('emails/confirmacion_pedido.html', context)
        text_content = strip_tags(html_content)
        
        subject = f'Pedido Confirmado - #{pedido.numero_pedido}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = pedido.usuario.email
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print(f"[DEBUG] ✓ Confirmación enviada exitosamente\n")
        
        logger.info(f"Confirmación enviada a {to_email} para pedido #{pedido.numero_pedido}")
        return True
        
    except Exception as e:
        print(f"[ERROR] ✗ Error enviando confirmación: {str(e)}\n")
        logger.error(f"Error al enviar confirmación: {str(e)}")
        return False


def enviar_notificacion_envio(pedido):
    """
    Envía notificación cuando el pedido es enviado
    """
    try:
        print(f"\n[DEBUG] Enviando notificación de envío pedido #{pedido.numero_pedido} a {pedido.usuario.email}")
        
        context = {
            'pedido': pedido,
            'usuario': pedido.usuario,
            'numero_seguimiento': pedido.numero_seguimiento,
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string('emails/notificacion_envio.html', context)
        text_content = strip_tags(html_content)
        
        subject = f'Tu Pedido ha sido Enviado - #{pedido.numero_pedido}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = pedido.usuario.email
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print(f"[DEBUG] ✓ Notificación de envío enviada exitosamente\n")
        
        logger.info(f"Notificación de envío a {to_email} para pedido #{pedido.numero_pedido}")
        return True
        
    except Exception as e:
        print(f"[ERROR] ✗ Error enviando notificación: {str(e)}\n")
        logger.error(f"Error al enviar notificación de envío: {str(e)}")
        return False
