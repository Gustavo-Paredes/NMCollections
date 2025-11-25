from django.urls import path
from . import views
from apps.productos import views as productos_views

app_name = 'core'

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    path('home/', views.HomeView.as_view(), name='home_template'),
    # Catálogo de productos
    path('catalogo/', productos_views.home, name='catalogo'),
    # Aquí puedes añadir otras rutas para tu app core
]