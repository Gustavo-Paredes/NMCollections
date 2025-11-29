from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel
from django.contrib.humanize.templatetags.humanize import intcomma


class Subasta(BaseModel):
    """
    Subastas de productos basado en tabla subasta del script.sql
    """
    ESTADO_SUBASTA_CHOICES = [
        ('en preparación', 'En Preparación'),
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
        ('retrasada', 'Retrasada'),
        ('en revisión', 'En revisión'),
    ]
    
    producto = models.ForeignKey(
        'productos.Producto', 
        on_delete=models.CASCADE, 
        related_name='subastas',
        verbose_name='Producto',
        null=True, blank=True 
    )

    fecha_inicio = models.DateTimeField(default=timezone.now, verbose_name='Fecha de inicio')
    fecha_fin = models.DateTimeField(verbose_name='Fecha de fin')
    precio_inicial = models.IntegerField(verbose_name='Precio inicial')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_SUBASTA_CHOICES,
        default='en preparación',
        verbose_name='Estado'
    )
    
    # Campos adicionales
    incremento_minimo = models.IntegerField(
        default=1,
        verbose_name='Incremento mínimo'
    )
    precio_reserva = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Precio de reserva'
    )
    ganador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subastas_ganadas',
        verbose_name='Ganador'
    )
    
    class Meta:
        verbose_name = 'Subasta'
        verbose_name_plural = 'Subastas'
        db_table = 'subasta'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Subasta de {self.producto.nombre} - {self.estado}"
    
    def actualizar_estado(self):
        """
        Cambia automáticamente el estado según fechas y situación de compra.
        """
        ahora = timezone.now()

        # Normalizar y evitar re-procesar si ya está finalizada/cancelada
        # NOTA: no bloqueamos el re-procesado cuando la subasta está 'en revisión'
        # porque un admin podría editar las fechas y reactivar la subasta.
        estado_norm = (self.estado or '').lower()
        if any(k in estado_norm for k in ['cancelada', 'finalizada', 'cerrada']):
            return  # no procesa subastas ya terminadas/canceladas

        # Si aún no empieza
        if ahora < self.fecha_inicio:
            nuevo_estado = 'en preparación'

        # Si está entre fecha de inicio y fin
        elif self.fecha_inicio <= ahora <= self.fecha_fin:
            nuevo_estado = 'activa'

        elif ahora > self.fecha_fin:
            # Si ya terminó, marcamos como 'en revisión' para que el ganador pueda pagar
            nuevo_estado = 'en revisión'

        # Si ya terminó y tiene un ganador confirmado, mantenemos 'en revisión' o 'finalizada'
        elif self.ganador:
            nuevo_estado = 'finalizada'

        else:
            nuevo_estado = self.estado  # sin cambio

        if nuevo_estado != self.estado:
            # Si cambiamos a 'en revisión' (terminó el tiempo), determinamos el ganador
            if nuevo_estado == 'en revisión' and not self.ganador:
                ultima_puja = self.pujas.order_by('-monto').first()
                if ultima_puja and (not self.precio_reserva or ultima_puja.monto >= self.precio_reserva):
                    self.ganador = ultima_puja.usuario
            
            self.estado = nuevo_estado
            self.save()
    
    @property
    def esta_activa(self):
        """Verifica si la subasta está activa y vigente"""
        ahora = timezone.now()
        return (self.estado == 'activa' and 
                self.fecha_inicio <= ahora <= self.fecha_fin)
    
    @property
    def precio_actual(self):
        """Retorna el precio actual de la subasta (última puja o precio inicial)"""
        ultima_puja = self.pujas.order_by('-monto').first()
        return ultima_puja.monto if ultima_puja else self.precio_inicial
    
    @property
    def total_pujas(self):
        """Retorna el total de pujas realizadas"""
        return self.pujas.count()
    
    def finalizar_subasta(self):
        """Finaliza la subasta y determina el ganador"""
        if self.estado != 'activa':
            return
        
        ultima_puja = self.pujas.order_by('-monto').first()
        if ultima_puja and (not self.precio_reserva or ultima_puja.monto >= self.precio_reserva):
            self.ganador = ultima_puja.usuario
        # Tras finalizar, colocamos la subasta en revisión para permitir el proceso de pago
        self.estado = 'en revisión'
        self.save()

    @property
    def puja_ganadora(self):
        """Retorna la puja ganadora (última por monto) o None"""
        return self.pujas.order_by('-monto').first()
    
    def puede_pujar(self, usuario, monto):
        """Verifica si un usuario puede realizar una puja válida."""
        ahora = timezone.now()
    
        # Verifica si está activa
        if not self.esta_activa:
            return False, "La subasta no está activa."
    
        # Evita que el ganador vuelva a pujar
        if self.ganador == usuario:
            return False, "Ya eres el ganador actual de esta subasta."
    
        # Verifica monto mínimo
        if monto < self.precio_actual + self.incremento_minimo:
            return False, f"La puja mínima debe ser de ${self.precio_actual + self.incremento_minimo}."
    
        # Opcional: puedes agregar límite máximo, control de usuarios, etc.
        return True, "Puja válida."
    


class Puja(BaseModel):
    """
    Pujas en subastas basado en tabla puja del script.sql
    """
    subasta = models.ForeignKey(
        Subasta, 
        on_delete=models.CASCADE, 
        related_name='pujas',
        verbose_name='Subasta'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='pujas',
        verbose_name='Usuario'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Monto')
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha')
    
    # Campos adicionales
    activa = models.BooleanField(default=True, verbose_name='Activa')
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP de origen')
    
    class Meta:
        verbose_name = 'Puja'
        verbose_name_plural = 'Pujas'
        db_table = 'puja'
        ordering = ['-fecha']
        unique_together = ['subasta', 'usuario', 'monto']  # Evitar pujas duplicadas
    
    def __str__(self):
        try:
            monto_display = intcomma(int(self.monto))
        except Exception:
            monto_display = self.monto
        return f"Puja de ${monto_display} por {self.usuario.email} en {self.subasta.producto.nombre}"
    
    def save(self, *args, **kwargs):
        # Validar que la puja sea válida antes de guardarla
        if not self.pk:  # Solo para nuevas pujas
            puede_pujar, mensaje = self.subasta.puede_pujar(self.usuario, self.monto)
            if not puede_pujar:
                raise ValueError(mensaje)
        
        super().save(*args, **kwargs)


# Modelo adicional para historial de pujas automáticas
class PujaAutomatica(BaseModel):
    """
    Sistema de pujas automáticas para usuarios
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='pujas_automaticas'
    )
    subasta = models.ForeignKey(
        Subasta, 
        on_delete=models.CASCADE, 
        related_name='pujas_automaticas'
    )
    monto_maximo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto máximo')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        verbose_name = 'Puja Automática'
        verbose_name_plural = 'Pujas Automáticas'
        unique_together = ['usuario', 'subasta']
    
    def __str__(self):
        return f"Puja automática de {self.usuario.email} hasta ${self.monto_maximo}"


# Modelo para notificaciones de subasta
class NotificacionSubasta(BaseModel):
    """
    Notificaciones relacionadas con subastas
    """
    TIPO_NOTIFICACION_CHOICES = [
        ('nueva_puja', 'Nueva puja realizada'),
        ('superado', 'Has sido superado'),
        ('ganaste', 'Ganaste la subasta'),
        ('finalizada', 'Subasta finalizada'),
        ('proximafin', 'Subasta próxima a finalizar'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subasta = models.ForeignKey(Subasta, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_NOTIFICACION_CHOICES)
    mensaje = models.TextField(verbose_name='Mensaje')
    leida = models.BooleanField(default=False, verbose_name='Leída')
    enviada_email = models.BooleanField(default=False, verbose_name='Enviada por email')
    
    class Meta:
        verbose_name = 'Notificación de Subasta'
        verbose_name_plural = 'Notificaciones de Subasta'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notificación para {self.usuario.email}: {self.tipo}"


class MensajeSubasta(BaseModel):
    """
    Mensajes de chat en subastas (reemplazo de WebSocket)
    """
    subasta = models.ForeignKey(
        Subasta, 
        on_delete=models.CASCADE, 
        related_name='mensajes',
        verbose_name='Subasta'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mensajes_subasta',
        verbose_name='Usuario'
    )
    mensaje = models.TextField(verbose_name='Mensaje')
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha')
    
    class Meta:
        verbose_name = 'Mensaje de Subasta'
        verbose_name_plural = 'Mensajes de Subasta'
        db_table = 'mensaje_subasta'
        ordering = ['fecha']
    
    def __str__(self):
        return f"{self.usuario.username}: {self.mensaje[:50]}"