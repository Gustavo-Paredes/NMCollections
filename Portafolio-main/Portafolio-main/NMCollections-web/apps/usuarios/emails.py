"""
Módulo para envío de correos relacionados con usuarios
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import logging

logger = logging.getLogger(__name__)


def enviar_correo_recuperacion(usuario, request=None):
    """
    Envía correo de recuperación de contraseña
    
    Args:
        usuario: Instancia del modelo Usuario
        request: Request de Django (opcional, para construir URL absoluta)
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        print(f"\n{'='*60}")
        print(f"[DEBUG] Iniciando envío de recuperación de contraseña")
        print(f"[DEBUG] Usuario: {usuario.username}")
        print(f"[DEBUG] Email destino: {usuario.email}")
        
        # Generar token único
        token = default_token_generator.make_token(usuario)
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        
        print(f"[DEBUG] Token generado correctamente")
        print(f"[DEBUG] UID: {uid}")
        
        # Construir URL de recuperación
        if request:
            site_url = request.build_absolute_uri('/')[:-1]
        else:
            site_url = settings.SITE_URL
        
        reset_url = f"{site_url}/usuarios/restablecer-password/{uid}/{token}/"
        
        print(f"[DEBUG] URL de recuperación: {reset_url}")
        
        # Contexto para el template
        context = {
            'usuario': usuario,
            'reset_url': reset_url,
            'site_url': site_url,
        }
        
        # Renderizar templates
        html_content = render_to_string('emails/recuperacion_password.html', context)
        text_content = strip_tags(html_content)
        
        print(f"[DEBUG] Template renderizado correctamente")
        
        # Crear email
        subject = 'Recuperación de Contraseña - NM Collections'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = usuario.email
        
        print(f"[DEBUG] From: {from_email}")
        print(f"[DEBUG] To: {to_email}")
        print(f"[DEBUG] Subject: {subject}")
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        
        print(f"[DEBUG] Email preparado, enviando...")
        
        email.send()
        
        print(f"[DEBUG] ✓ Correo de recuperación enviado exitosamente")
        print(f"{'='*60}\n")
        
        logger.info(f"Correo de recuperación enviado a {to_email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] ✗ Falló el envío del correo de recuperación")
        print(f"[ERROR] Tipo de error: {type(e).__name__}")
        print(f"[ERROR] Mensaje: {str(e)}")
        print(f"{'='*60}\n")
        logger.error(f"Error al enviar correo de recuperación: {str(e)}")
        return False


def enviar_bienvenida(usuario):
    """
    Envía correo de bienvenida a nuevo usuario
    """
    try:
        context = {
            'usuario': usuario,
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string('emails/bienvenida.html', context)
        text_content = strip_tags(html_content)
        
        subject = '¡Bienvenido a NM Collections!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = usuario.email
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Correo de bienvenida enviado a {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar correo de bienvenida: {str(e)}")
        return False
