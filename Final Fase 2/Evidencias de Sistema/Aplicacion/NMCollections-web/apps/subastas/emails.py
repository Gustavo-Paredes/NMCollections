from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.shortcuts import reverse


def enviar_email_ganador_subasta(subasta, request=None):
    """Envía un email al ganador cuando la subasta pasa a 'En revisión'."""
    try:
        usuario = subasta.ganador
        if not usuario or not usuario.email:
            return False

        # Construir URL absoluta a la página de pago
        if request:
            site_url = request.build_absolute_uri('/')[:-1]
        else:
            site_url = getattr(settings, 'SITE_URL', '')

        # Apuntar a una página GET que muestre el formulario de pago y posteé
        # al endpoint POST que inicia la compra (`pedidos:comprar_subasta`).
        pagar_url = f"{site_url}{reverse('subastas:pagar', args=[subasta.id])}"

        context = {
            'usuario': usuario,
            'subasta': subasta,
            'puja_ganadora': subasta.puja_ganadora,
            'pagar_url': pagar_url,
            'site_url': site_url,
        }

        html_content = render_to_string('emails/subasta_ganador.html', context)
        text_content = strip_tags(html_content)

        subject = f"Has ganado la subasta: {subasta.producto.nombre}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = usuario.email

        email = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=[to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return True
    except Exception as e:
        print(f"Error enviando email ganador subasta: {e}")
        return False
