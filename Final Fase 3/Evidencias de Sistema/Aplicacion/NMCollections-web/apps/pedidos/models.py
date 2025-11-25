from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel, EstadoPedidoChoices
import uuid


class Pedido(BaseModel):
    """
    Pedidos de compra basado en tabla pedido del script.sql
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='pedidos',
        verbose_name='Usuario'
    )
    fecha_pedido = models.DateTimeField(default=timezone.now, verbose_name='Fecha del pedido')
    estado = models.CharField(
        max_length=20,
        choices=EstadoPedidoChoices.choices,
        default=EstadoPedidoChoices.PENDIENTE,
        verbose_name='Estado'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Total')
    metodo_pago = models.CharField(max_length=50, blank=True, verbose_name='Método de pago')
    direccion_envio = models.TextField(blank=True, verbose_name='Dirección de envío')
    notas = models.TextField(blank=True, verbose_name='Notas')
    
    # Campos adicionales para tracking
    numero_pedido = models.CharField(max_length=20, unique=True, blank=True, verbose_name='Número de pedido')
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de confirmación')
    fecha_envio = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de envío')
    numero_seguimiento = models.CharField(max_length=100, blank=True, verbose_name='Número de seguimiento')
    
    # Relación con subasta (si el pedido proviene de una subasta ganada)
    subasta = models.ForeignKey(
        'subastas.Subasta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
        verbose_name='Subasta',
        help_text='Subasta asociada a este pedido (si aplica)'
    )
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        db_table = 'pedido'
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido {self.numero_pedido or self.id} - {self.usuario.email}"
    
    def save(self, *args, **kwargs):
        # Generar número de pedido automáticamente
        if not self.numero_pedido:
            self.numero_pedido = self.generar_numero_pedido()
        super().save(*args, **kwargs)
    
    def generar_numero_pedido(self):
        """Genera un número único de pedido"""
        return f"PED-{uuid.uuid4().hex[:8].upper()}"
    
    def calcular_total(self):
        """Calcula el total del pedido basado en sus productos"""
        total = sum(item.precio_total for item in self.productos.all())
        self.total = total
        self.save()
        return total


class PedidoProducto(BaseModel):
    """
    Productos en un pedido basado en tabla pedido_producto del script.sql
    """
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='productos',
        verbose_name='Pedido'
    )
    producto = models.ForeignKey(
        'productos.Producto', 
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    cantidad = models.IntegerField(verbose_name='Cantidad')
    personalizacion = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='Personalización'
    )
    # Nueva relación directa con CartaPersonalizada
    carta_personalizada = models.ForeignKey(
        'personalizacion.CartaPersonalizada',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Carta Personalizada',
        help_text='Carta personalizada asociada a este producto del pedido'
    )
    imagen_pedido = models.ImageField(
        upload_to='pedidos/',
        null=True,
        blank=True,
        verbose_name='Imagen del pedido',
        help_text='Snapshot de la imagen (producto o carta personalizada) en el momento de la compra'
    )
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio total')
    
    class Meta:
        verbose_name = 'Producto en Pedido'
        verbose_name_plural = 'Productos en Pedido'
        db_table = 'pedido_producto'
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - Pedido {self.pedido.numero_pedido}"
    
    def save(self, *args, **kwargs):
        # Calcular precio total automáticamente si no se especifica
        if not self.precio_total:
            self.precio_total = self.cantidad * self.producto.precio_base
        # Intentar asignar imagen_pedido si está vacía
        if not self.imagen_pedido:
            try:
                if self.carta_personalizada and getattr(self.carta_personalizada, 'imagen_frente', None):
                    # Usar imagen de la carta personalizada
                    self.imagen_pedido = self.carta_personalizada.imagen_frente
                elif getattr(self.producto, 'imagen_referencia', None):
                    self.imagen_pedido = self.producto.imagen_referencia
            except Exception:
                pass
        super().save(*args, **kwargs)


# Modelo adicional para historial de estados (no está en script original)
class HistorialEstadoPedido(BaseModel):
    """
    Historial de cambios de estado del pedido
    """
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='historial_estados'
    )
    estado_anterior = models.CharField(
        max_length=20,
        choices=EstadoPedidoChoices.choices,
        null=True,
        blank=True,
        verbose_name='Estado anterior'
    )
    estado_nuevo = models.CharField(
        max_length=20,
        choices=EstadoPedidoChoices.choices,
        verbose_name='Estado nuevo'
    )
    fecha_cambio = models.DateTimeField(default=timezone.now, verbose_name='Fecha del cambio')
    usuario_cambio = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario que realizó el cambio'
    )
    comentarios = models.TextField(blank=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"Pedido {self.pedido.numero_pedido}: {self.estado_anterior} -> {self.estado_nuevo}"