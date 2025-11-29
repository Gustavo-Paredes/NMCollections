from django.contrib import admin
from .models import (
    Plantilla, PlantillaElemento, PlantillaFondo,
    CartaPersonalizada, CartaParametro
)


class PlantillaElementoInline(admin.TabularInline):
    model = PlantillaElemento
    extra = 1
    fields = ['nombre_parametro', 'tipo_elemento', 'posicion_x', 'posicion_y', 'ancho', 'alto', 'fuente', 'color', 'z_index']


class PlantillaFondoInline(admin.TabularInline):
    model = PlantillaFondo
    extra = 1
    fields = ['tipo_fondo', 'valor']


@admin.register(Plantilla)
class PlantillaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_carta', 'diseñador', 'estado', 'usuario_creador', 'fecha_creacion']
    list_filter = ['estado', 'tipo_carta', 'diseñador', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'diseñador']
    readonly_fields = ['fecha_creacion']
    inlines = [PlantillaElementoInline, PlantillaFondoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo_carta')
        }),
        ('Marco del Diseñador', {
            'fields': ('imagen_marco', 'ancho_marco', 'alto_marco', 'diseñador', 'archivo_original'),
            'description': 'Subir imagen de marco creada por el diseñador'
        }),
        ('Configuración', {
            'fields': ('estado', 'usuario_creador')
        }),
        ('Compatibilidad Legacy', {
            'fields': ('imagen_preview',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Si no hay usuario creador, asignar el usuario actual
        if not obj.usuario_creador:
            obj.usuario_creador = request.user
        super().save_model(request, obj, form, change)


class CartaParametroInline(admin.TabularInline):
    model = CartaParametro
    extra = 1
    fields = ['nombre_parametro', 'tipo_parametro', 'valor']


@admin.register(CartaPersonalizada)
class CartaPersonalizadaAdmin(admin.ModelAdmin):
    list_display = ['nombre_carta', 'usuario', 'plantilla', 'estado', 'fecha_creacion', 'ruta_imagen']
    list_filter = ['estado', 'plantilla__tipo_carta', 'fecha_creacion']
    search_fields = ['nombre_carta', 'usuario__nombre', 'usuario__correo']
    readonly_fields = ['fecha_creacion', 'ruta_imagen']
    inlines = [CartaParametroInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_carta', 'usuario', 'plantilla')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Imagen generada', {
            'fields': ('ruta_imagen',),
            'description': 'Ruta del archivo generado por el canvas'
        }),
        ('Metadata', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlantillaElemento)
class PlantillaElementoAdmin(admin.ModelAdmin):
    list_display = ['plantilla', 'nombre_parametro', 'tipo_elemento', 'posicion_x', 'posicion_y']
    list_filter = ['tipo_elemento', 'plantilla']
    search_fields = ['nombre_parametro', 'plantilla__nombre']


@admin.register(PlantillaFondo)
class PlantillaFondoAdmin(admin.ModelAdmin):
    list_display = ['plantilla', 'tipo_fondo']
    list_filter = ['tipo_fondo']
    search_fields = ['plantilla__nombre']


@admin.register(CartaParametro)
class CartaParametroAdmin(admin.ModelAdmin):
    list_display = ['carta', 'nombre_parametro', 'tipo_parametro']
    list_filter = ['tipo_parametro']
    search_fields = ['nombre_parametro', 'carta__nombre_carta']
