from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_diseñador

# Router para las APIs REST
router = DefaultRouter()
router.register(r'plantillas', views.PlantillaViewSet)
router.register(r'cartas', views.CartaPersonalizadaViewSet, basename='carta')
router.register(r'canvas-editor', views.CanvasEditorView, basename='canvas-editor')

app_name = 'personalizacion'

urlpatterns = [
    # API REST endpoints
    path('', include(router.urls)),
    
    # Panel de diseñador (solo para admins)
    path('panel-diseñador/', views_diseñador.panel_diseñador, name='panel_diseñador'),
    path('crear-plantilla/', views_diseñador.crear_plantilla, name='crear_plantilla'),
    path('editar-plantilla/<int:plantilla_id>/', views_diseñador.editar_plantilla, name='editar_plantilla'),
    path('eliminar-plantilla/<int:plantilla_id>/', views_diseñador.eliminar_plantilla, name='eliminar_plantilla'),
    path('agregar-elemento/<int:plantilla_id>/', views_diseñador.agregar_elemento, name='agregar_elemento'),
    path('eliminar-elemento/<int:elemento_id>/', views_diseñador.eliminar_elemento, name='eliminar_elemento'),
    path('cambiar-estado-plantilla/<int:plantilla_id>/', views_diseñador.cambiar_estado_plantilla, name='cambiar_estado_plantilla'),
    
    # Vista del editor de canvas (requiere login)
    path('canvas-editor/', views.canvas_editor, name='canvas_editor'),
    
    # Gestión de cartas del usuario
    path('mis-cartas/', views.mis_cartas, name='mis_cartas'),
    path('editar-carta/<int:carta_id>/', views.editar_carta, name='editar_carta'),
    path('finalizar-carta/<int:carta_id>/', views.finalizar_carta, name='finalizar_carta'),
    path('eliminar-carta/<int:carta_id>/', views.eliminar_carta, name='eliminar_carta'),
    path('guardar-imagen/<int:carta_id>/', views.guardar_imagen_carta, name='guardar_imagen_carta'),
    path('vista-previa/<int:carta_id>/', views.vista_previa_carta, name='vista_previa_carta'),
    path('crear-pedido/<int:carta_id>/', views.crear_pedido_carta, name='crear_pedido_carta'),
    path('duplicar-carta/<int:carta_id>/', views.duplicar_carta, name='duplicar_carta'),
    
    # Vista del perfil con cartas del usuario (legacy)
    path('perfil/', views.perfil_cartas, name='perfil_cartas'),
]