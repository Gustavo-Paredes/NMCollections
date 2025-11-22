from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import Rol, Usuario, Sesion, PerfilUsuario


class UsuarioCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios"""
    
    class Meta:
        model = Usuario
        fields = ('email', 'first_name', 'last_name', 'rol')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer username opcional en el formulario
        if 'username' in self.fields:
            self.fields['username'].required = False
            self.fields['username'].help_text = "Se generará automáticamente si se deja vacío"


class UsuarioChangeForm(UserChangeForm):
    """Formulario personalizado para editar usuarios"""
    
    class Meta:
        model = Usuario
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].help_text = "Identificador único del usuario (se genera automáticamente)"


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    
    list_display = ['email', 'first_name', 'last_name', 'rol', 'estado', 'fecha_registro']
    list_filter = ['estado', 'rol', 'fecha_registro', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'apellido_materno', 'username']
    ordering = ['-fecha_registro']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'apellido_materno', 'telefono', 'direccion')
        }),
        ('Permisos', {
            'fields': ('rol', 'estado', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas Importantes', {'fields': ('last_login', 'fecha_registro')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'rol', 'password1', 'password2'),
            'description': 'El username se generará automáticamente basado en el correo si se deja vacío'
        }),
    )
    
    readonly_fields = ['fecha_registro', 'last_login']
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado desde el admin"""
        # Si no se proporciona username, se generará automáticamente en el método save del modelo
        if not obj.username and obj.email:
            pass  # El método save del modelo se encargará
        super().save_model(request, obj, form, change)


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'dispositivo', 'estado', 'fecha_inicio', 'fecha_expiracion', 'ip_origen']
    list_filter = ['estado', 'dispositivo', 'fecha_inicio']
    search_fields = ['usuario__email', 'ip_origen']
    readonly_fields = ['fecha_inicio', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False  # Las sesiones se crean automáticamente


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'notificaciones_email', 'notificaciones_push', 'perfil_publico']
    list_filter = ['notificaciones_email', 'notificaciones_push', 'perfil_publico', 'newsletter']
    search_fields = ['usuario__email', 'biografia']
    readonly_fields = ['created_at', 'updated_at']