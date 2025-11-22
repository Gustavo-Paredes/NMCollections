from django.db import models
from apps.usuarios.models import Usuario
import os

def plantilla_marco_path(instance, filename):
    """Función para generar la ruta de subida de marcos de plantillas"""
    return f'plantillas/marcos/{instance.tipo_carta}/{filename}'

def carta_imagen_path(instance, filename):
    """Función para generar la ruta de subida de imágenes de cartas"""
    return f'cartas/{instance.usuario.id}/{filename}'

class Plantilla(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tipo_carta = models.CharField(max_length=50, blank=True, null=True)
    
    # NUEVO: Campo para subir imagen de marco del diseñador
    imagen_marco = models.ImageField(
        upload_to=plantilla_marco_path,
        blank=True, 
        null=True,
        help_text="Imagen de marco/fondo creada por el diseñador"
    )
    
    # Mantener campo legacy para compatibilidad
    imagen_preview = models.CharField(max_length=255, blank=True, null=True)
    
    # NUEVO: Metadatos del marco
    ancho_marco = models.IntegerField(default=320, help_text="Ancho del marco en píxeles")
    alto_marco = models.IntegerField(default=420, help_text="Alto del marco en píxeles")
    
    # NUEVO: Información del diseñador
    diseñador = models.CharField(max_length=100, blank=True, null=True, help_text="Nombre del diseñador")
    archivo_original = models.CharField(max_length=255, blank=True, null=True, help_text="Nombre del archivo original")
    
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activa')
    usuario_creador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'plantilla'
        
    def __str__(self):
        return self.nombre
    
    @property
    def imagen_marco_url(self):
        """URL de la imagen del marco"""
        if self.imagen_marco:
            return self.imagen_marco.url
        return self.imagen_preview

class PlantillaElemento(models.Model):
    TIPO_ELEMENTO_CHOICES = [
        ('texto', 'Texto'),
        ('imagen', 'Imagen'),
        ('color', 'Color'),
        ('numero', 'Número'),
    ]
    
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE)
    nombre_parametro = models.CharField(max_length=50, blank=True, null=True)
    tipo_elemento = models.CharField(max_length=10, choices=TIPO_ELEMENTO_CHOICES)
    posicion_x = models.IntegerField(blank=True, null=True)
    posicion_y = models.IntegerField(blank=True, null=True)
    ancho = models.IntegerField(blank=True, null=True)
    alto = models.IntegerField(blank=True, null=True)
    fuente = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    z_index = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'plantilla_elemento'
        
    def __str__(self):
        return f"{self.plantilla.nombre} - {self.nombre_parametro}"

class PlantillaFondo(models.Model):
    TIPO_FONDO_CHOICES = [
        ('color', 'Color'),
        ('imagen', 'Imagen'),
        ('gradiente', 'Gradiente'),
    ]
    
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE)
    tipo_fondo = models.CharField(max_length=10, choices=TIPO_FONDO_CHOICES)
    valor = models.TextField()
    
    class Meta:
        db_table = 'plantilla_fondo'
        
    def __str__(self):
        return f"{self.plantilla.nombre} - {self.tipo_fondo}"

class CartaPersonalizada(models.Model):
    ESTADO_CHOICES = [
        ('en_edicion', 'En Edición'),
        ('finalizada', 'Finalizada'),
        ('comprada', 'Comprada'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE)
    nombre_carta = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='en_edicion')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # NUEVO: Campo para la imagen generada del canvas
    imagen_generada = models.ImageField(
        upload_to=carta_imagen_path,
        blank=True, 
        null=True,
        help_text="Imagen PNG generada del canvas de la carta"
    )
    # NUEVO: Campo para guardar la ruta de la imagen generada
    ruta_imagen = models.CharField(max_length=255, blank=True, null=True, help_text="Ruta de la imagen generada del canvas")
    
    class Meta:
        db_table = 'carta_personalizada'
        
    def __str__(self):
        return f"{self.nombre_carta or 'Carta sin nombre'} - {self.usuario.first_name}"

class CartaParametro(models.Model):
    TIPO_PARAMETRO_CHOICES = [
        ('texto', 'Texto'),
        ('imagen', 'Imagen'),
        ('color', 'Color'),
        ('numero', 'Número'),
    ]
    
    carta = models.ForeignKey(CartaPersonalizada, on_delete=models.CASCADE)
    nombre_parametro = models.CharField(max_length=50)
    tipo_parametro = models.CharField(max_length=10, choices=TIPO_PARAMETRO_CHOICES)
    valor = models.TextField()
    
    class Meta:
        db_table = 'carta_parametro'
        
    def __str__(self):
        return f"{self.carta.nombre_carta} - {self.nombre_parametro}"
