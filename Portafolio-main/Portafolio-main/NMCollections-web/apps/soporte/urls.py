from django.urls import path
from . import views

app_name = 'soporte'

urlpatterns = (
    [
        path('mi-soporte/', views.user_chat_view, name='mi_soporte'),
        path('admin/threads/', views.admin_threads_view, name='admin_threads'),
        path('admin/threads/<int:thread_id>/', views.admin_thread_chat_view, name='admin_thread_chat'),
        # API endpoints
        path('thread/me/', views.api_my_thread, name='api_my_thread'),
        path('messages/<int:thread_id>/', views.api_messages, name='api_messages'),
    ]
)
