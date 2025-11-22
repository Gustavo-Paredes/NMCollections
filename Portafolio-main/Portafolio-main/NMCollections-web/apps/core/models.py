from django.db import models
from django.utils import timezone
from django.conf import settings


class BaseModel(models.Model):
    """
    Modelo base con campos comunes para todas las entidades
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """
    Modelo base con timestamps para auditoría
    """
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        abstract = True


# Choices reutilizables en todo el sistema
class EstadoChoices(models.TextChoices):
    ACTIVO = 'activo', 'Activo'
    INACTIVO = 'inactivo', 'Inactivo'
    BLOQUEADO = 'bloqueado', 'Bloqueado'
    PENDIENTE = 'pendiente', 'Pendiente'
    SUSPENDIDO = 'suspendido', 'Suspendido'


class DispositivoChoices(models.TextChoices):
    WEB = 'web', 'Web'
    ANDROID = 'android', 'Android'
    IOS = 'ios', 'iOS'


class TipoProductoChoices(models.TextChoices):
    ESTANDAR = 'estandar', 'Estándar'

    DIGITAL = 'digital', 'Digital'


class EstadoPedidoChoices(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    CONFIRMADO = 'confirmado', 'Confirmado'
    ENVIADO = 'enviado', 'Enviado'
    COMPLETADO = 'completado', 'Completado'
    ANULADO = 'anulado', 'Anulado'


class EstadoPagoChoices(models.TextChoices):
    APROBADO = 'aprobado', 'Aprobado'
    PENDIENTE = 'pendiente', 'Pendiente'
    FALLIDO = 'fallido', 'Fallido'
    REEMBOLSADO = 'reembolsado', 'Reembolsado'


# Modelo de configuración global
class Configuracion(BaseModel):
    """
    Configuraciones globales del sistema
    """
    clave = models.CharField(max_length=100, unique=True, verbose_name='Clave')
    valor = models.TextField(verbose_name='Valor')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    tipo = models.CharField(max_length=20, choices=[
        ('string', 'Texto'),
        ('integer', 'Entero'),
        ('float', 'Decimal'),
        ('boolean', 'Booleano'),
        ('json', 'JSON'),
    ], default='string', verbose_name='Tipo de dato')
    
    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
    
    def __str__(self):
        return f"{self.clave}: {self.valor}"


# Log de auditoría transversal
class LogActividad(BaseModel):
    """
    Log de actividades del sistema para auditoría
    """
    usuario = models.ForeignKey(
        'usuarios.Usuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Usuario'
    )
    accion = models.CharField(max_length=100, verbose_name='Acción')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    objeto_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='ID del objeto')
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP de origen')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    datos_anteriores = models.JSONField(null=True, blank=True, verbose_name='Datos anteriores')
    datos_nuevos = models.JSONField(null=True, blank=True, verbose_name='Datos nuevos')
    
    class Meta:
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.accion} en {self.modelo} por {self.usuario or 'Sistema'}"


# =========================================
# MÓDULO QR / NFC (del script.sql)
# =========================================

class QR(BaseModel):
    """
    Códigos QR basado en tabla qr del script.sql
    """
    producto = models.ForeignKey(
        'productos.Producto', 
        on_delete=models.CASCADE, 
        related_name='codigos_qr',
        verbose_name='Producto'
    )
    codigo_qr = models.CharField(max_length=100, unique=True, verbose_name='Código QR')
    url_redireccion = models.CharField(max_length=255, blank=True, verbose_name='URL de redirección')
    fecha_generacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de generación')
    estado = models.CharField(
        max_length=20,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo',
        verbose_name='Estado'
    )
    
    class Meta:
        verbose_name = 'Código QR'
        verbose_name_plural = 'Códigos QR'
        db_table = 'qr'
    
    def __str__(self):
        return f"QR {self.codigo_qr} - {self.producto.nombre}"


class QRLog(BaseModel):
    """
    Log de actividad de códigos QR basado en tabla qr_log del script.sql
    """
    ACCION_CHOICES = [
        ('escaneo', 'Escaneo'),
        ('redireccion', 'Redirección'),
    ]
    
    qr = models.ForeignKey(QR, on_delete=models.CASCADE, related_name='logs', verbose_name='Código QR')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Usuario'
    )
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES, verbose_name='Acción')
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha')
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP de origen')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    
    class Meta:
        verbose_name = 'Log de QR'
        verbose_name_plural = 'Logs de QR'
        db_table = 'qr_log'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"QR {self.qr.codigo_qr} - {self.accion} - {self.fecha}"


class NFC(BaseModel):
    """
    Códigos NFC basado en tabla nfc del script.sql
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='codigos_nfc',
        verbose_name='Usuario',
        null=True,
        blank=True
    )
    producto = models.ForeignKey(
        'productos.Producto', 
        on_delete=models.CASCADE, 
        related_name='codigos_nfc',
        verbose_name='Producto'
    )
    codigo_nfc = models.CharField(max_length=100, unique=True, verbose_name='Código NFC')
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
            ('en_transferencia', 'En transferencia'),
            ('reclamada', 'Reclamada'),
        ],
        default='activo',
        verbose_name='Estado'
    )
    fecha_asignacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de asignación')
    
    class Meta:
        verbose_name = 'Código NFC'
        verbose_name_plural = 'Códigos NFC'
        db_table = 'nfc'
    
    def __str__(self):
        usuario_email = self.usuario.email if self.usuario else "Sin usuario"
        producto_nombre = self.producto.nombre if self.producto else "Sin producto"
        return f"NFC {self.codigo_nfc} - {usuario_email} - {producto_nombre}"


class NFCLog(BaseModel):
    """
    Log de actividad de códigos NFC basado en tabla nfc_log del script.sql
    """
    ACCION_CHOICES = [
        ('escaneo', 'Escaneo'),
        ('registro', 'Registro'),
        ('validacion', 'Validación'),
        ('transferencia_iniciada', 'Transferencia iniciada'),
        ('transferencia_reclamada', 'Transferencia reclamada'),
    ]
    
    nfc = models.ForeignKey(NFC, on_delete=models.CASCADE, related_name='logs', verbose_name='Código NFC')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Usuario'
    )
    accion = models.CharField(max_length=30, choices=ACCION_CHOICES, verbose_name='Acción')
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha')
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP de origen')
    datos_adicionales = models.JSONField(null=True, blank=True, verbose_name='Datos adicionales')
    
    class Meta:
        verbose_name = 'Log de NFC'
        verbose_name_plural = 'Logs de NFC'
        db_table = 'nfc_log'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"NFC {self.nfc.codigo_nfc} - {self.accion} - {self.fecha}"