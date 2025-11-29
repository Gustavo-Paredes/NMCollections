from django.urls import path
from . import views
from . import api as views_api
from . import views_informes
from . import views_reportes

app_name = 'pedidos'

urlpatterns = [
    # Panel de administración (solo staff)
    path('panel/', views.panel_pedidos, name='panel_pedidos'),
    path('lista/', views.lista_pedidos, name='lista_pedidos'),
    path('detalle/<int:pedido_id>/', views.detalle_pedido_admin, name='detalle_pedido_admin'),
    path('cambiar-estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('acciones-masivas/', views.acciones_masivas_pedidos, name='acciones_masivas_pedidos'),
    path('descargar-pdf/<int:pedido_id>/', views.descargar_pedido_pdf, name='descargar_pedido_pdf'),
    path('enviar-mensaje/<int:pedido_id>/', views.enviar_mensaje_cliente, name='enviar_mensaje_cliente'),
    
    # Vista para usuarios normales
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mi-pedido/<int:pedido_id>/', views.detalle_pedido_usuario, name='detalle_pedido_usuario'),
    path('cancelar/<int:pedido_id>/', views.cancelar_pedido_usuario, name='cancelar_pedido_usuario'),
    path('confirmar-entrega/<int:pedido_id>/', views.confirmar_entrega_usuario, name='confirmar_entrega_usuario'),
    
    # API
    path('estadisticas/', views.api_estadisticas_pedidos, name='api_estadisticas'),
    
    # Legacy
    path('crear-carta/', views.crear_carta_view, name='crear_carta'),
    
    # Informes y reportes
    path('informe-ventas/', views_informes.descargar_informe_ventas, name='informe_ventas'),
    path('informe-ventas-excel/', views_informes.descargar_informe_ventas_excel, name='informe_ventas_excel'),
    path('informe-ventas-pdf/', views_informes.descargar_informe_ventas_pdf, name='informe_ventas_pdf'),
    path('reportes/', views_reportes.reportes_admin, name='reportes_admin'),
    path('reportes/api/', views_reportes.reportes_admin_api, name='reportes_admin_api'),
    
    # Compras con WebPay
    path('comprar-producto/<int:producto_id>/', views.comprar_producto, name='comprar_producto'),
    path('comprar-carrito/', views.comprar_carrito, name='comprar_carrito'),
    path('comprar-subasta/<int:subasta_id>/', views.comprar_subasta, name='comprar_subasta'),
    
    # Gestión de pedidos
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<str:numero_pedido>/', views.detalle_pedido, name='detalle_pedido'),
    # API endpoint para todos los pedidos (solo admin/diseñador)
    path('all/', views_api.PedidoAllListAPIView.as_view(), name='pedidos_all'),
]