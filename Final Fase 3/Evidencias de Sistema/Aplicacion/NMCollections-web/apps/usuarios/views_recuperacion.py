"""
Vista para recuperación de contraseña
"""
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .emails import enviar_correo_recuperacion

Usuario = get_user_model()


@require_http_methods(["GET", "POST"])
def solicitar_recuperacion(request):
    """
    Vista para solicitar recuperación de contraseña
    """
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        
        try:
            usuario = Usuario.objects.get(correo=correo)
            # Enviar correo de recuperación
            if enviar_correo_recuperacion(usuario, request):
                messages.success(
                    request,
                    'Se ha enviado un correo con instrucciones para restablecer tu contraseña.'
                )
            else:
                messages.error(
                    request,
                    'Hubo un error al enviar el correo. Por favor intenta de nuevo.'
                )
        except Usuario.DoesNotExist:
            # Por seguridad, no revelar si el correo existe o no
            messages.success(
                request,
                'Si el correo existe, recibirás instrucciones para restablecer tu contraseña.'
            )
        
        return redirect('usuarios:login')
    
    return render(request, 'usuarios/solicitar_recuperacion.html')


@require_http_methods(["GET", "POST"])
def restablecer_password(request, uidb64, token):
    """
    Vista para restablecer la contraseña con el token
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    
    # Verificar que el token sea válido
    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password1 == password2:
                usuario.set_password(password1)
                usuario.save()
                messages.success(request, 'Contraseña restablecida exitosamente. Ya puedes iniciar sesión.')
                return redirect('usuarios:login')
            else:
                messages.error(request, 'Las contraseñas no coinciden.')
        
        return render(request, 'usuarios/restablecer_password.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    else:
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return render(request, 'usuarios/restablecer_password.html', {'validlink': False})
