from django.contrib import admin
from .models import (
    MiniJuego, Partida, ProgresoJuego, Logro
)


@admin.register(MiniJuego)
class MiniJuegoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'tipo', 'activo', 'total_partidas', 
        'jugadores_unicos', 'fecha_creacion'
    ]
    list_filter = ['tipo', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = [
        'total_partidas', 'jugadores_unicos', 'fecha_creacion',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'descripcion', 'activo')
        }),
        ('Configuración', {
            'fields': (
                'imagen_icono', 'configuracion', 'puntaje_maximo', 'tiempo_limite'
            ),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('total_partidas', 'jugadores_unicos'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = [
        'juego', 'player1', 'player2', 'resultado', 'ganador',
        'fecha_inicio', 'fecha_fin', 'esta_en_curso'
    ]
    list_filter = ['resultado', 'fecha_inicio', 'juego']
    search_fields = [
        'juego__nombre', 'player1__correo', 'player2__correo',
        'ganador__correo'
    ]
    readonly_fields = [
        'fecha_inicio', 'esta_en_curso', 'duracion_segundos',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información de la Partida', {
            'fields': ('juego', 'player1', 'player2')
        }),
        ('Resultado', {
            'fields': ('resultado', 'ganador', 'puntaje_player1', 'puntaje_player2')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'duracion_segundos')
        }),
        ('Datos Adicionales', {
            'fields': ('datos_partida',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProgresoJuego)
class ProgresoJuegoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'juego', 'nivel', 'puntaje_total', 
        'partidas_jugadas', 'partidas_ganadas', 'porcentaje_victoria'
    ]
    list_filter = ['juego', 'nivel']
    search_fields = ['usuario__correo', 'juego__nombre']
    readonly_fields = [
        'porcentaje_victoria', 'fecha_actualizacion',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información', {
            'fields': ('usuario', 'juego')
        }),
        ('Progreso', {
            'fields': ('nivel', 'puntaje_total', 'mejor_puntaje')
        }),
        ('Estadísticas', {
            'fields': (
                'partidas_jugadas', 'partidas_ganadas', 'porcentaje_victoria',
                'tiempo_total_jugado'
            )
        }),
        ('Logros', {
            'fields': ('logros',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['actualizar_niveles']
    
    def actualizar_niveles(self, request, queryset):
        count = 0
        for progreso in queryset:
            if progreso.actualizar_nivel():
                count += 1
        self.message_user(request, f"Se actualizaron {count} niveles.")
    actualizar_niveles.short_description = "Actualizar niveles según puntaje"


@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'juego', 'tipo', 'puntos_recompensa', 'activo'
    ]
    list_filter = ['tipo', 'activo', 'juego']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']