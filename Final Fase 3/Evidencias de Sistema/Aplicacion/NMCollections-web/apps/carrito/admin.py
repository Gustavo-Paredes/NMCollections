from django.contrib import admin
from .models import Carrito, CarritoProducto, ListaDeseos, ProductoListaDeseos


class CarritoProductoInline(admin.TabularInline):
    model = CarritoProducto
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'estado', 'fecha_creacion', 'total_productos', 'total_precio']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['usuario__correo']
    readonly_fields = ['fecha_creacion', 'total_productos', 'total_precio', 'created_at', 'updated_at']
    inlines = [CarritoProductoInline]


@admin.register(CarritoProducto)
class CarritoProductoAdmin(admin.ModelAdmin):
    list_display = ['carrito', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['carrito__usuario__correo', 'producto__nombre']
    readonly_fields = ['subtotal', 'created_at', 'updated_at']


class ProductoListaDeseosInline(admin.TabularInline):
    model = ProductoListaDeseos
    extra = 0


@admin.register(ListaDeseos)
class ListaDeseosAdmin(admin.ModelAdmin):
    list_display = ['usuario']
    search_fields = ['usuario__correo']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductoListaDeseosInline]


@admin.register(ProductoListaDeseos)
class ProductoListaDeseosAdmin(admin.ModelAdmin):
    list_display = ['lista_deseos', 'producto', 'fecha_agregado']
    search_fields = ['lista_deseos__usuario__correo', 'producto__nombre']
    readonly_fields = ['fecha_agregado', 'created_at', 'updated_at']