from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, PerfilUsuario, DireccionUsuario
from apps.soporte.models import SupportThread
from .forms import LoginForm, RegisterForm, ProfileForm, DireccionForm, UserUpdateForm

class LoginView(TemplateView):
    template_name = 'usuarios/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('usuarios:dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            # Autenticar usando email como USERNAME_FIELD
            user = authenticate(request, username=email, password=password)
                    
            if user:
                login(request, user)
                # Guardar tokens JWT en sesión
                refresh = RefreshToken.for_user(user)
                request.session['access_token'] = str(refresh.access_token)
                request.session['refresh_token'] = str(refresh)
                
                messages.success(request, f'¡Bienvenido {user.first_name}!')
                return redirect('usuarios:dashboard')
            else:
                messages.error(request, 'Email o contraseña incorrectos')
        else:
            messages.error(request, 'Por favor completa todos los campos')
        
        return render(request, self.template_name)

class RegisterView(TemplateView):
    template_name = 'usuarios/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('usuarios:dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        telefono = request.POST.get('telefono', '')
        
        # Validaciones
        if not all([first_name, last_name, email, password, password_confirm]):
            messages.error(request, 'Por favor completa todos los campos')
            return render(request, self.template_name)
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, self.template_name)
        
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe un usuario con este email')
            return render(request, self.template_name)
        
        try:
            # Crear usuario
            from apps.usuarios.models import Rol
            rol_cliente = Rol.objects.get_or_create(nombre='cliente')[0]
            
            user = Usuario.objects.create_user(
                username=email,  # Usar email como username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                rol=rol_cliente
            )
            # Guardar teléfono opcional en el usuario
            if telefono:
                user.telefono = telefono
                user.save(update_fields=["telefono"])
            
            # Crear perfil (sin teléfono, se guarda en Usuario)
            PerfilUsuario.objects.create(
                usuario=user,
                fecha_nacimiento=None
            )
            
            messages.success(request, '¡Cuenta creada exitosamente! Puedes iniciar sesión')
            return redirect('usuarios:login')
            
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
            return render(request, self.template_name)

@login_required
def dashboard_view(request):
    """Dashboard principal después del login"""
    context = {
        'user': request.user,
        'perfil': getattr(request.user, 'perfilusuario', None)
    }
    # Si es staff, preparar resumen de soporte
    if request.user.is_staff:
        threads_qs = SupportThread.objects.select_related('user', 'assigned_admin')\
            .order_by('-updated_at')
        context.update({
            'support_recent_threads': list(threads_qs[:5]),
            'support_open_count': threads_qs.filter(status='open').count(),
            'support_unassigned_count': threads_qs.filter(status='open', assigned_admin__isnull=True).count(),
        })
    return render(request, 'usuarios/dashboard.html', context)

@login_required 
def profile_view(request):
    """Vista del perfil del usuario"""
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        # Manejar eliminación de avatar
        if 'eliminar_avatar' in request.POST:
            if perfil.avatar:
                perfil.avatar.delete()
                perfil.save()
                messages.success(request, 'Foto de perfil eliminada correctamente')
            return redirect('usuarios:profile')
        
        # Manejar cambio de avatar desde modal
        if 'cambiar_avatar' in request.POST and request.FILES.get('avatar'):
            perfil.avatar = request.FILES['avatar']
            perfil.save()
            messages.success(request, 'Foto de perfil actualizada correctamente')
            return redirect('usuarios:profile')
        
        # Manejar actualización normal del perfil
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=perfil)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('usuarios:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=perfil)
    
    context = {
        'user': request.user,
        'perfil': perfil,
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'usuarios/profile.html', context)

@login_required
def addresses_view(request):
    """Vista para ver las direcciones del usuario"""
    direcciones = DireccionUsuario.objects.filter(usuario=request.user)
    context = {
        'direcciones': direcciones
    }
    return render(request, 'usuarios/addresses.html', context)

@login_required
def add_address_view(request):
    """Vista para agregar dirección"""
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.usuario = request.user
            direccion.save()
            
            messages.success(request, 'Dirección agregada correctamente')
            return redirect('usuarios:addresses')
    else:
        form = DireccionForm()
    
    context = {
        'form': form,
        'title': 'Agregar Dirección'
    }
    return render(request, 'usuarios/address_form.html', context)

@login_required
def edit_address_view(request, address_id):
    """Vista para editar dirección"""
    direccion = get_object_or_404(DireccionUsuario, id=address_id, usuario=request.user)
    
    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada correctamente')
            return redirect('usuarios:addresses')
    else:
        form = DireccionForm(instance=direccion)
    
    context = {
        'form': form,
        'title': 'Editar Dirección',
        'direccion': direccion
    }
    return render(request, 'usuarios/address_form.html', context)

@login_required
def delete_address_view(request, address_id):
    """Vista para eliminar dirección"""
    direccion = get_object_or_404(DireccionUsuario, id=address_id, usuario=request.user)
    
    if request.method == 'POST':
        direccion.delete()
        messages.success(request, 'Dirección eliminada correctamente')
    
    return redirect('usuarios:addresses')

def logout_view(request):
    """Logout y limpiar sesión"""
    logout(request)
    messages.success(request, '¡Hasta pronto!')
    return redirect('core:home')