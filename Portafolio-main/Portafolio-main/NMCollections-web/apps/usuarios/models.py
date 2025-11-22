from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel, EstadoChoices, DispositivoChoices


class Rol(BaseModel):
    """
    Roles del sistema basado en tabla rol del script.sql
    """
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre del rol')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        db_table = 'rol'
    
    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    """
    Usuario personalizado basado en tabla usuario del script.sql
    Extiende AbstractUser para mantener compatibilidad con Django auth
    
    NOTA: Usamos los campos heredados de AbstractUser y los mapeamos:
    - first_name -> nombre
    - last_name -> apellido_paterno  
    - email -> correo
    """
    # Sobrescribir email para hacerlo único (requerido por USERNAME_FIELD)
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    
    # Campos adicionales específicos
    apellido_materno = models.CharField(max_length=50, blank=True, verbose_name='Apellido materno')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.TextField(blank=True, verbose_name='Dirección')
    
    # Relaciones
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, verbose_name='Rol')
    
    # Estado y fechas
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name='Fecha de registro')
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.ACTIVO,
        verbose_name='Estado'
    )
    
    # Configurar email como campo de autenticación
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuario'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    # Propiedades para compatibilidad con código existente
    @property
    def nombre(self):
        """Alias para first_name"""
        return self.first_name
    
    @nombre.setter
    def nombre(self, value):
        self.first_name = value
    
    @property
    def apellido_paterno(self):
        """Alias para last_name"""
        return self.last_name
    
    @apellido_paterno.setter
    def apellido_paterno(self, value):
        self.last_name = value
    
    @property
    def correo(self):
        """Alias para email"""
        return self.email
    
    @correo.setter
    def correo(self, value):
        self.email = value
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        nombres = [self.first_name, self.last_name]
        if self.apellido_materno:
            nombres.append(self.apellido_materno)
        return ' '.join(filter(None, nombres))
    
    def save(self, *args, **kwargs):
        # Generar username único basado en email si no existe
        if not self.username and self.email:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            # Verificar que el username sea único
            while Usuario.objects.filter(username=username).exclude(pk=self.pk).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            self.username = username
        
        super().save(*args, **kwargs)


class Sesion(BaseModel):
    """
    Control de sesiones y tokens basado en tabla sesion del script.sql
    """
    ESTADO_SESION_CHOICES = [
        ('activa', 'Activa'),
        ('expirada', 'Expirada'),
        ('cerrada', 'Cerrada'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones', verbose_name='Usuario')
    token = models.CharField(max_length=255, unique=True, verbose_name='Token de sesión')
    fecha_inicio = models.DateTimeField(default=timezone.now, verbose_name='Fecha de inicio')
    fecha_expiracion = models.DateTimeField(verbose_name='Fecha de expiración')
    ip_origen = models.GenericIPAddressField(verbose_name='IP de origen')
    dispositivo = models.CharField(
        max_length=20,
        choices=DispositivoChoices.choices,
        verbose_name='Dispositivo'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_SESION_CHOICES,
        default='activa',
        verbose_name='Estado de la sesión'
    )
    
    class Meta:
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'
        db_table = 'sesion'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Sesión de {self.usuario.email} desde {self.dispositivo}"
    
    def is_expired(self):
        """Verifica si la sesión ha expirado"""
        return timezone.now() > self.fecha_expiracion
    
    def close_session(self):
        """Cierra la sesión"""
        self.estado = 'cerrada'
        self.save()


# Modelo de perfil extendido (opcional, para datos adicionales)
class PerfilUsuario(BaseModel):
    """
    Perfil extendido del usuario para datos adicionales
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='Avatar')
    biografia = models.TextField(max_length=500, blank=True, verbose_name='Biografía')
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    
    # Configuraciones de notificaciones
    notificaciones_email = models.BooleanField(default=True, verbose_name='Notificaciones por email')
    notificaciones_push = models.BooleanField(default=True, verbose_name='Notificaciones push')
    newsletter = models.BooleanField(default=False, verbose_name='Suscrito a newsletter')
    
    # Configuraciones de privacidad
    perfil_publico = models.BooleanField(default=True, verbose_name='Perfil público')
    mostrar_estadisticas = models.BooleanField(default=True, verbose_name='Mostrar estadísticas de juegos')
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"Perfil de {self.usuario.email}"


class DireccionUsuario(models.Model):
    """Modelo para almacenar direcciones de usuarios"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='direcciones')
    nombre = models.CharField("Nombre de dirección", max_length=100, help_text="Ej: Casa, Trabajo")
    direccion = models.TextField("Dirección completa")
    ciudad = models.CharField(max_length=100)
    region = models.CharField("Región", max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=100, default="Chile")
    telefono = models.CharField(max_length=20)
    es_principal = models.BooleanField("Dirección principal", default=False)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        ordering = ['-es_principal', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.usuario.email}"
    
    def save(self, *args, **kwargs):
        # Si es principal, quitar principal de otras direcciones del usuario
        if self.es_principal:
            DireccionUsuario.objects.filter(
                usuario=self.usuario, 
                es_principal=True
            ).exclude(id=self.id).update(es_principal=False)
        super().save(*args, **kwargs)