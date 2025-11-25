from django.contrib import admin
from .models import (
    TransaccionPago, MetodoPago, TarjetaUsuario, ReembolsoTransaccion
)


@admin.register(TransaccionPago)
class TransaccionPagoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'pedido', 'monto', 'metodo_pago', 'estado', 
        'fecha_transaccion', 'es_exitosa'
    ]
    list_filter = ['estado', 'metodo_pago', 'fecha_transaccion']
    search_fields = [
        'pedido__numero_pedido', 'codigo_autorizacion', 
        'gateway_transaction_id'
    ]
    readonly_fields = [
        'fecha_transaccion', 'es_exitosa', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('pedido', 'monto', 'metodo_pago', 'estado')
        }),
        ('Detalles de la Transacción', {
            'fields': (
                'fecha_transaccion', 'codigo_autorizacion', 
                'gateway_transaction_id', 'gateway_response_code'
            )
        }),
        ('Respuesta del Gateway', {
            'fields': ('gateway_response_message', 'detalle_response'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TarjetaUsuario)
class TarjetaUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'alias', 'tipo_tarjeta', 'ultimos_4_digitos', 
        'fecha_expiracion', 'activa'
    ]
    list_filter = ['tipo_tarjeta', 'activa', 'fecha_expiracion']
    search_fields = ['usuario__correo', 'alias', 'ultimos_4_digitos']
    readonly_fields = ['token_gateway', 'created_at', 'updated_at']


@admin.register(ReembolsoTransaccion)
class ReembolsoTransaccionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'transaccion_original', 'monto_reembolso', 'estado',
        'fecha_solicitud', 'fecha_procesado'
    ]
    list_filter = ['estado', 'fecha_solicitud']
    search_fields = [
        'transaccion_original__pedido__numero_pedido', 
        'codigo_reembolso'
    ]
    readonly_fields = ['fecha_solicitud', 'created_at', 'updated_at']