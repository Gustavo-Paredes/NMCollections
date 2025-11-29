from django.contrib import admin
from .models import SupportThread, SupportMessage


@admin.register(SupportThread)
class SupportThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'assigned_admin', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__correo', 'user__username', 'assigned_admin__correo')
    autocomplete_fields = ('user', 'assigned_admin')


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'sender', 'short_content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'sender__correo', 'thread__user__correo')
    autocomplete_fields = ('thread', 'sender')

    def short_content(self, obj):
        return (obj.content[:60] + '...') if len(obj.content) > 60 else obj.content
        
    short_content.short_description = 'Contenido'
