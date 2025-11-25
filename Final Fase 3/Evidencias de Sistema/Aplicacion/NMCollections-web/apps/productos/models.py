from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel, TipoProductoChoices, EstadoChoices


class CategoriaProducto(BaseModel):
    """
    Categorías de productos basado en tabla categoria_producto del script.sql
    """
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    
    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Producto'
        db_table = 'categoria_producto'
    
    def __str__(self):
        return self.nombre


class Producto(BaseModel):
    """
    Productos principales basado en tabla producto del script.sql
    """
    ESTADO_PRODUCTO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('descontinuado', 'Descontinuado'),
    ]
    
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    categoria = models.ForeignKey(
        CategoriaProducto, 
        on_delete=models.PROTECT, 
        verbose_name='Categoría'
    )
    precio_base = models.IntegerField(verbose_name='Precio base')
    stock = models.IntegerField(null=True, blank=True, verbose_name='Stock')
    tipo = models.CharField(
        max_length=20,
        choices=TipoProductoChoices.choices,
        verbose_name='Tipo de producto'
    )
    imagen_referencia = models.ImageField(upload_to='productos/', blank=True, verbose_name='Imagen de referencia')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PRODUCTO_CHOICES,
        default='activo',
        verbose_name='Estado'
    )
    # Nueva relación con cartas personalizadas
    carta = models.ForeignKey(
        'personalizacion.CartaPersonalizada',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Carta Personalizada'
    )
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        db_table = 'producto'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    @property
    def disponible(self):
        """Verifica si el producto está disponible"""
        if self.tipo == 'digital':
            return self.estado == 'activo'
        return self.estado == 'activo' and (self.stock is None or self.stock > 0)


class ProductoPersonalizacion(BaseModel):
    """
    Opciones de personalización para productos basado en tabla producto_personalizacion del script.sql
    """
    OPCION_TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('texto', 'Texto'),
        ('color', 'Color'),
        ('estilo', 'Estilo'),
    ]
    
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name='personalizaciones',
        verbose_name='Producto'
    )
    opcion_tipo = models.CharField(
        max_length=20,
        choices=OPCION_TIPO_CHOICES,
        verbose_name='Tipo de opción'
    )
    valor = models.CharField(max_length=255, verbose_name='Valor')
    preview_url = models.CharField(max_length=255, blank=True, verbose_name='URL de vista previa')
    
    class Meta:
        verbose_name = 'Personalización de Producto'
        verbose_name_plural = 'Personalizaciones de Producto'
        db_table = 'producto_personalizacion'
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.opcion_tipo}: {self.valor}"


# Modelos adicionales para completar funcionalidad (no están en script.sql original)
class ImagenProducto(BaseModel):
    """
    Imágenes adicionales de productos
    """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/', verbose_name='Imagen')
    alt_text = models.CharField(max_length=200, verbose_name='Texto alternativo')
    es_principal = models.BooleanField(default=False, verbose_name='Imagen principal')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Producto'
        ordering = ['orden']
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class ResenaProducto(BaseModel):
    """
    Reseñas de productos
    """
    CALIFICACION_CHOICES = [
        (1, '1 estrella'),
        (2, '2 estrellas'),
        (3, '3 estrellas'),
        (4, '4 estrellas'),
        (5, '5 estrellas'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    calificacion = models.PositiveIntegerField(choices=CALIFICACION_CHOICES, verbose_name='Calificación')
    titulo = models.CharField(max_length=200, verbose_name='Título')
    comentario = models.TextField(verbose_name='Comentario')
    compra_verificada = models.BooleanField(default=False, verbose_name='Compra verificada')
    
    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        unique_together = ['producto', 'usuario']
    
    def __str__(self):
        return f"Reseña de {self.usuario.email} para {self.producto.nombre}"