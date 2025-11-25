from django.urls import path
from . import views

app_name = 'subastas'

urlpatterns = [
    # Página principal de subastas
    path('', views.SubastaView.as_view(), name='subasta'),
    path('<int:subasta_id>/', views.SubastaDetalleView.as_view(), name='detalle'),
    path('eliminar/<int:subasta_id>/', views.eliminar_subasta, name='eliminar'),
    path('admin/', views.SubastaAdminView.as_view(), name='admin_subastas'),
    
    # API Endpoints (Reemplazo de WebSockets)
    path('api/<int:subasta_id>/pujas/', views.api_obtener_pujas, name='api_pujas'),
    path('api/<int:subasta_id>/mensajes/', views.api_obtener_mensajes, name='api_mensajes'),
    path('api/<int:subasta_id>/enviar-mensaje/', views.api_enviar_mensaje, name='api_enviar_mensaje'),
]