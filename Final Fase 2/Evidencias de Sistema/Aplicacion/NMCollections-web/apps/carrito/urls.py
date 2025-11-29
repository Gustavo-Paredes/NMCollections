from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    # Vista principal del carrito
    path('', views.ver_carrito, name='ver_carrito'),
    
    # Operaciones del carrito
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar'),
    path('actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar'),
    path('vaciar/', views.vaciar_carrito, name='vaciar'),
    
    # API para obtener cantidad
    path('cantidad/', views.obtener_cantidad_carrito, name='cantidad_api'),

    # Agregar carta personalizada al carrito
    path('agregar-carta/<int:carta_id>/', views.agregar_carta_personalizada, name='agregar_carta_personalizada'),
]
