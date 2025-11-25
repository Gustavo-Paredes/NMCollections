from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth import authenticate
from .models import Usuario, PerfilUsuario, DireccionUsuario
import re

class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu email',
            'required': True,
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
            'required': True
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            # Usamos el email como nombre de usuario para la autenticación
            user = authenticate(username=email, password=password)
            if not user:
                # Intentar con el campo email directamente
                try:
                    user_obj = Usuario.objects.get(email=email)
                    user = authenticate(username=user_obj.username, password=password)
                except Usuario.DoesNotExist:
                    user = None
                    
            if not user:
                raise forms.ValidationError('Email o contraseña incorrectos')
            if not user.is_active:
                raise forms.ValidationError('Esta cuenta está desactivada')
        
        return cleaned_data

class RegisterForm(forms.ModelForm):
    """Formulario de registro de usuario"""
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Crea una contraseña segura',
            'required': True
        }),
        min_length=8,
        help_text='Mínimo 8 caracteres'
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña',
            'required': True
        })
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': 'Debes aceptar los términos y condiciones'
        }
    )
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Tu apellido',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu-email@ejemplo.com',
                'required': True
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este email')
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Validaciones de contraseña
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Za-z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra')
            
        if not re.search(r'\d', password):
            raise forms.ValidationError('La contraseña debe contener al menos un número')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data

class ProfileForm(forms.ModelForm):
    """Formulario para actualizar perfil del usuario"""
    
    class Meta:
        model = PerfilUsuario
        fields = ['fecha_nacimiento', 'avatar', 'biografia', 'notificaciones_email', 'notificaciones_push', 'newsletter', 'perfil_publico', 'mostrar_estadisticas']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cuéntanos sobre ti'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'notificaciones_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notificaciones_push': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'newsletter': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'perfil_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_estadisticas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class UserUpdateForm(forms.ModelForm):
    """Formulario para actualizar datos básicos del usuario"""
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        required=True,
        validators=[UnicodeUsernameValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre de usuario'
        }),
        help_text='Letras, números y @/./+/-/_'
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificar que el email no esté en uso por otro usuario
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este email ya está en uso por otro usuario')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Asegurar unicidad del username entre usuarios
        if Usuario.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso')
        return username

class ChangePasswordForm(forms.Form):
    """Formulario para cambiar contraseña"""
    current_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña actual'
        })
    )
    new_password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        min_length=8
    )
    confirm_password = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma la nueva contraseña'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('La contraseña actual no es correcta')
        return current_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data

class DireccionForm(forms.ModelForm):
    """Formulario para direcciones del usuario"""
    
    class Meta:
        model = DireccionUsuario
        fields = ['nombre', 'direccion', 'ciudad', 'region', 'codigo_postal', 'pais', 'telefono', 'es_principal']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Casa, Oficina, etc.'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Calle, número, comuna'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Chile'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'es_principal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }