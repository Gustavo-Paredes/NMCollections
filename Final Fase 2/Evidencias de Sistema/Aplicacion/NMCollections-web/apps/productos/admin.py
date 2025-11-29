from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    CategoriaProducto, Producto, ProductoPersonalizacion,
    ImagenProducto, ResenaProducto
)


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']


class ProductoPersonalizacionInline(admin.TabularInline):
    model = ProductoPersonalizacion
    extra = 1


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'preview_imagen', 'alt_text', 'orden', 'es_principal']
    readonly_fields = ['preview_imagen']
    
    def preview_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 4px;" />', obj.imagen.url)
        return '-'
    preview_imagen.short_description = 'Vista previa'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_base', 'stock', 'tipo', 'estado', 'disponible']
    list_filter = ['categoria', 'tipo', 'estado', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'disponible', 'created_at', 'updated_at']
    inlines = [ProductoPersonalizacionInline, ImagenProductoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'tipo')
        }),
        ('Precio y Stock', {
            'fields': ('precio_base', 'stock')
        }),
        ('Estado', {
            'fields': ('estado', 'imagen_referencia')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductoPersonalizacion)
class ProductoPersonalizacionAdmin(admin.ModelAdmin):
    list_display = ['producto', 'opcion_tipo', 'valor']
    list_filter = ['opcion_tipo']
    search_fields = ['producto__nombre', 'valor']


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'preview_imagen', 'alt_text', 'es_principal', 'orden']
    list_filter = ['es_principal']
    search_fields = ['producto__nombre', 'alt_text']
    list_editable = ['orden']
    
    def preview_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 60px; border-radius: 4px;" />', obj.imagen.url)
        return '-'
    preview_imagen.short_description = 'Imagen'


@admin.register(ResenaProducto)
class ResenaProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'calificacion', 'compra_verificada', 'created_at']
    list_filter = ['calificacion', 'compra_verificada', 'created_at']
    search_fields = ['producto__nombre', 'usuario__correo', 'titulo']
    readonly_fields = ['created_at', 'updated_at']