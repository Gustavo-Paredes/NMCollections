from django.contrib import admin
from .models import Pedido, PedidoProducto, HistorialEstadoPedido


class PedidoProductoInline(admin.TabularInline):
    model = PedidoProducto
    extra = 0
    readonly_fields = ['precio_total']


class HistorialEstadoPedidoInline(admin.TabularInline):
    model = HistorialEstadoPedido
    extra = 0
    readonly_fields = ['fecha_cambio']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_pedido', 'usuario', 'estado', 'total', 
        'fecha_pedido', 'metodo_pago'
    ]
    list_filter = ['estado', 'fecha_pedido', 'metodo_pago']
    search_fields = ['numero_pedido', 'usuario__correo', 'usuario__nombre']
    readonly_fields = [
        'numero_pedido', 'fecha_pedido', 'fecha_confirmacion', 
        'fecha_envio', 'created_at', 'updated_at'
    ]
    inlines = [PedidoProductoInline, HistorialEstadoPedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'estado', 'fecha_pedido')
        }),
        ('Detalles de Pago', {
            'fields': ('total', 'metodo_pago')
        }),
        ('Envío', {
            'fields': ('direccion_envio', 'numero_seguimiento', 'fecha_confirmacion', 'fecha_envio')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'estado' in form.changed_data:
            # Crear historial cuando cambia el estado
            HistorialEstadoPedido.objects.create(
                pedido=obj,
                estado_anterior=form.initial.get('estado'),
                estado_nuevo=obj.estado,
                usuario_cambio=request.user,
                comentarios=f"Estado cambiado desde Django Admin por {request.user.email}"
            )
        super().save_model(request, obj, form, change)


@admin.register(PedidoProducto)
class PedidoProductoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad', 'precio_total', 'personalizacion']
    search_fields = ['pedido__numero_pedido', 'producto__nombre']
    readonly_fields = ['precio_total', 'personalizacion', 'created_at', 'updated_at']


@admin.register(HistorialEstadoPedido)
class HistorialEstadoPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario_cambio']
    list_filter = ['estado_nuevo', 'fecha_cambio']
    search_fields = ['pedido__numero_pedido']
    readonly_fields = ['fecha_cambio', 'created_at', 'updated_at']