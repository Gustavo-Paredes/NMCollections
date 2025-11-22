from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    # Página principal de productos
    path('', views.ProductoListView.as_view(), name='lista'),
    path('<int:producto_id>/', views.ProductoDetalleView.as_view(), name='detalle'),
    
    # Gestión de productos
    path('gestionar/', views.GestionarProductosView.as_view(), name='gestionar'),
    path('crear/', views.CrearProductoView.as_view(), name='crear'),
    path('editar/<int:pk>/', views.EditarProductoView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', views.EliminarProductoView.as_view(), name='eliminar'),
    
    # API para obtener datos de producto
    path('<int:pk>/api/', views.ProductoAPIView.as_view(), name='api_detalle'),
]