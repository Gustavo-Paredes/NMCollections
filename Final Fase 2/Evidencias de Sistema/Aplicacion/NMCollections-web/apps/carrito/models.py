from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel


class Carrito(BaseModel):
    """
    Carrito de compras basado en tabla carrito del script.sql
    """
    ESTADO_CARRITO_CHOICES = [
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='carritos',
        verbose_name='Usuario'
    )
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CARRITO_CHOICES,
        default='activo',
        verbose_name='Estado'
    )
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        db_table = 'carrito'
    
    def __str__(self):
        return f"Carrito de {self.usuario.email} - {self.estado}"
    
    @property
    def total_productos(self):
        """Retorna el total de productos en el carrito"""
        return sum(item.cantidad for item in self.productos.all())
    
    @property
    def total_precio(self):
        """Retorna el precio total del carrito"""
        return sum(item.cantidad * item.precio_unitario for item in self.productos.all())


class CarritoProducto(BaseModel):
    """
    Productos en el carrito basado en tabla carrito_producto del script.sql
    """
    carrito = models.ForeignKey(
        Carrito, 
        on_delete=models.CASCADE, 
        related_name='productos',
        verbose_name='Carrito'
    )
    producto = models.ForeignKey(
        'productos.Producto', 
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    cantidad = models.IntegerField(verbose_name='Cantidad')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio unitario')
    personalizacion = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='Personalización'
    )
    
    class Meta:
        verbose_name = 'Producto en Carrito'
        verbose_name_plural = 'Productos en Carrito'
        db_table = 'carrito_producto'
        unique_together = ['carrito', 'producto']
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en carrito de {self.carrito.usuario.email}"
    
    @property
    def subtotal(self):
        """Retorna el subtotal de este item"""
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        # Si no se especifica precio unitario, usar el precio base del producto
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_base
        super().save(*args, **kwargs)


# Modelo adicional para wishlist (no está en script original pero es útil)
class ListaDeseos(BaseModel):
    """
    Lista de deseos del usuario
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='lista_deseos',
        verbose_name='Usuario'
    )
    
    class Meta:
        verbose_name = 'Lista de Deseos'
        verbose_name_plural = 'Listas de Deseos'
    
    def __str__(self):
        return f"Lista de deseos de {self.usuario.email}"


class ProductoListaDeseos(BaseModel):
    """
    Productos en la lista de deseos
    """
    lista_deseos = models.ForeignKey(
        ListaDeseos, 
        on_delete=models.CASCADE, 
        related_name='productos'
    )
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(default=timezone.now, verbose_name='Fecha agregado')
    
    class Meta:
        verbose_name = 'Producto en Lista de Deseos'
        verbose_name_plural = 'Productos en Lista de Deseos'
        unique_together = ['lista_deseos', 'producto']
    
    def __str__(self):
        return f"{self.producto.nombre} en lista de {self.lista_deseos.usuario.email}"