from django.contrib import admin
from .models import (
    Subasta, Puja, PujaAutomatica, NotificacionSubasta, MensajeSubasta
)


@admin.register(Subasta)
class SubastaAdmin(admin.ModelAdmin):
    list_display = [
        'producto', 'precio_inicial', 'precio_actual', 'estado',
        'fecha_inicio', 'fecha_fin', 'total_pujas', 'ganador'
    ]
    list_filter = ['estado', 'fecha_inicio', 'fecha_fin']
    search_fields = ['producto__nombre', 'ganador__correo']
    readonly_fields = [
        'precio_actual', 'total_pujas', 'esta_activa', 
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información de la Subasta', {
            'fields': ('producto', 'precio_inicial', 'incremento_minimo', 'precio_reserva')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Estado', {
            'fields': ('estado', 'ganador')
        }),
        ('Estadísticas', {
            'fields': ('precio_actual', 'total_pujas', 'esta_activa'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['finalizar_subastas']
    
    def finalizar_subastas(self, request, queryset):
        for subasta in queryset.filter(estado='activa'):
            subasta.finalizar_subasta()
        self.message_user(request, f"Se finalizaron {len(queryset)} subastas.")
    finalizar_subastas.short_description = "Finalizar subastas seleccionadas"


@admin.register(Puja)
class PujaAdmin(admin.ModelAdmin):
    list_display = ['subasta', 'usuario', 'monto', 'fecha', 'activa']
    list_filter = ['activa', 'fecha']
    search_fields = ['subasta__producto__nombre', 'usuario__correo']
    readonly_fields = ['fecha', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False  # Las pujas se crean a través de la API


@admin.register(PujaAutomatica)
class PujaAutomaticaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'subasta', 'monto_maximo', 'activa']
    list_filter = ['activa']
    search_fields = ['usuario__correo', 'subasta__producto__nombre']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificacionSubasta)
class NotificacionSubastaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'subasta', 'tipo', 'leida', 'enviada_email', 'created_at']
    list_filter = ['tipo', 'leida', 'enviada_email', 'created_at']
    search_fields = ['usuario__correo', 'subasta__producto__nombre']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MensajeSubasta)
class MensajeSubastaAdmin(admin.ModelAdmin):
    list_display = ['subasta', 'usuario', 'mensaje_corto', 'fecha']
    list_filter = ['fecha', 'subasta']
    search_fields = ['usuario__username', 'mensaje', 'subasta__producto__nombre']
    readonly_fields = ['fecha', 'created_at', 'updated_at']
    
    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'
    
    def has_add_permission(self, request):
        return False  # Los mensajes se crean a través de la API