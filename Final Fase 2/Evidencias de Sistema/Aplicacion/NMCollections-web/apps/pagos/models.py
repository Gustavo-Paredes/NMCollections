from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel, EstadoPagoChoices


class TransaccionPago(BaseModel):
    """
    Transacciones de pago basado en tabla transaccion_pago del script.sql
    """
    pedido = models.ForeignKey(
        'pedidos.Pedido', 
        on_delete=models.CASCADE, 
        related_name='transacciones',
        verbose_name='Pedido'
    )
    fecha_transaccion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de transacción')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    metodo_pago = models.CharField(max_length=50, blank=True, verbose_name='Método de pago')
    estado = models.CharField(
        max_length=20,
        choices=EstadoPagoChoices.choices,
        default=EstadoPagoChoices.PENDIENTE,
        verbose_name='Estado'
    )
    codigo_autorizacion = models.CharField(max_length=100, blank=True, verbose_name='Código de autorización')
    detalle_response = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='Detalle de respuesta'
    )
    
    # Campos adicionales para integración con gateways de pago
    gateway_transaction_id = models.CharField(max_length=255, blank=True, verbose_name='ID de transacción del gateway')
    gateway_response_code = models.CharField(max_length=50, blank=True, verbose_name='Código de respuesta del gateway')
    gateway_response_message = models.TextField(blank=True, verbose_name='Mensaje de respuesta del gateway')
    
    class Meta:
        verbose_name = 'Transacción de Pago'
        verbose_name_plural = 'Transacciones de Pago'
        db_table = 'transaccion_pago'
        ordering = ['-fecha_transaccion']
    
    def __str__(self):
        return f"Transacción {self.id} - Pedido {self.pedido.numero_pedido} - ${self.monto}"
    
    @property
    def es_exitosa(self):
        """Verifica si la transacción fue exitosa"""
        return self.estado == EstadoPagoChoices.APROBADO
    
    def marcar_como_aprobada(self, codigo_autorizacion=None):
        """Marca la transacción como aprobada"""
        self.estado = EstadoPagoChoices.APROBADO
        if codigo_autorizacion:
            self.codigo_autorizacion = codigo_autorizacion
        self.save()
    
    def marcar_como_fallida(self, razon=None):
        """Marca la transacción como fallida"""
        self.estado = EstadoPagoChoices.FALLIDO
        if razon and self.detalle_response:
            self.detalle_response['razon_fallo'] = razon
        elif razon:
            self.detalle_response = {'razon_fallo': razon}
        self.save()


# Modelos adicionales para completar funcionalidad de pagos
class MetodoPago(BaseModel):
    """
    Métodos de pago disponibles en el sistema
    """
    TIPO_CHOICES = [
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('wallet_digital', 'Billetera Digital'),
        ('crypto', 'Criptomoneda'),
        ('efectivo', 'Efectivo'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    configuracion = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='Configuración específica'
    )
    
    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
    
    def __str__(self):
        return self.nombre


class TarjetaUsuario(BaseModel):
    """
    Tarjetas guardadas de los usuarios (solo metadatos, no datos sensibles)
    """
    usuario = models.ForeignKey(
        'usuarios.Usuario', 
        on_delete=models.CASCADE, 
        related_name='tarjetas'
    )
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50, verbose_name='Alias')
    ultimos_4_digitos = models.CharField(max_length=4, verbose_name='Últimos 4 dígitos')
    tipo_tarjeta = models.CharField(max_length=20, verbose_name='Tipo de tarjeta')  # Visa, Mastercard, etc.
    fecha_expiracion = models.DateField(verbose_name='Fecha de expiración')
    token_gateway = models.CharField(max_length=255, verbose_name='Token del gateway')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        verbose_name = 'Tarjeta de Usuario'
        verbose_name_plural = 'Tarjetas de Usuario'
    
    def __str__(self):
        return f"{self.alias} - ****{self.ultimos_4_digitos}"


class ReembolsoTransaccion(BaseModel):
    """
    Reembolsos de transacciones
    """
    transaccion_original = models.ForeignKey(
        TransaccionPago, 
        on_delete=models.CASCADE, 
        related_name='reembolsos'
    )
    monto_reembolso = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto del reembolso')
    razon = models.TextField(verbose_name='Razón del reembolso')
    fecha_solicitud = models.DateTimeField(default=timezone.now, verbose_name='Fecha de solicitud')
    fecha_procesado = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de procesado')
    estado = models.CharField(
        max_length=20,
        choices=[
            ('solicitado', 'Solicitado'),
            ('procesando', 'Procesando'),
            ('completado', 'Completado'),
            ('rechazado', 'Rechazado'),
        ],
        default='solicitado',
        verbose_name='Estado'
    )
    codigo_reembolso = models.CharField(max_length=100, blank=True, verbose_name='Código de reembolso')
    
    class Meta:
        verbose_name = 'Reembolso'
        verbose_name_plural = 'Reembolsos'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Reembolso {self.id} - ${self.monto_reembolso} - {self.estado}"