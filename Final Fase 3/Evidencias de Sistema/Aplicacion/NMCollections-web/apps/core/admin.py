from django.contrib import admin
from .models import (
    Configuracion, LogActividad, QR, QRLog, NFC, NFCLog
)


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['clave', 'valor', 'tipo', 'descripcion']
    list_filter = ['tipo']
    search_fields = ['clave', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'modelo', 'objeto_id', 'created_at']
    list_filter = ['accion', 'modelo', 'created_at']
    search_fields = ['usuario__correo', 'accion', 'modelo']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(QR)
class QRAdmin(admin.ModelAdmin):
    list_display = ['codigo_qr', 'producto', 'estado', 'fecha_generacion']
    list_filter = ['estado', 'fecha_generacion']
    search_fields = ['codigo_qr', 'producto__nombre']
    readonly_fields = ['fecha_generacion', 'created_at', 'updated_at']


@admin.register(QRLog)
class QRLogAdmin(admin.ModelAdmin):
    list_display = ['qr', 'usuario', 'accion', 'fecha', 'ip_origen']
    list_filter = ['accion', 'fecha']
    search_fields = ['qr__codigo_qr', 'usuario__correo']
    readonly_fields = ['fecha', 'created_at', 'updated_at']


@admin.register(NFC)
class NFCAdmin(admin.ModelAdmin):
    list_display = ['codigo_nfc', 'usuario', 'producto', 'estado', 'fecha_asignacion']
    list_filter = ['estado', 'fecha_asignacion']
    search_fields = ['codigo_nfc', 'usuario__correo', 'producto__nombre']
    readonly_fields = ['fecha_asignacion', 'created_at', 'updated_at']


@admin.register(NFCLog)
class NFCLogAdmin(admin.ModelAdmin):
    list_display = ['nfc', 'usuario', 'accion', 'fecha', 'ip_origen']
    list_filter = ['accion', 'fecha']
    search_fields = ['nfc__codigo_nfc', 'usuario__correo']
    readonly_fields = ['fecha', 'created_at', 'updated_at']