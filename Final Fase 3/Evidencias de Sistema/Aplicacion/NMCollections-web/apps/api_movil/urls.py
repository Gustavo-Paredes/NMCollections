"""
URLs centralizadas del sistema
Router principal para toda la API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    # Usuarios
    UsuarioViewSet, RolViewSet,
    # Productos  
    ProductoViewSet, CategoriaProductoViewSet,
    # Carrito
    CarritoViewSet,
    # Pedidos
    PedidoViewSet,
    # Subastas
    SubastaViewSet,
    # NFT - Comentado (App eliminada)
    # WalletViewSet, NFTViewSet,
    # Juegos
    MiniJuegoViewSet, PartidaViewSet, ProgresoJuegoViewSet,
    # Core
    QRViewSet, NFCViewSet,
)

# Router principal de la API
router = DefaultRouter()

# Registrar todas las ViewSets
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'carrito', CarritoViewSet, basename='carrito')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'subastas', SubastaViewSet)
# router.register(r'wallets', WalletViewSet, basename='wallet')  # App NFT eliminada
# router.register(r'nfts', NFTViewSet, basename='nft')  # App NFT eliminada
router.register(r'juegos', MiniJuegoViewSet)
router.register(r'partidas', PartidaViewSet, basename='partida')
router.register(r'progreso-juegos', ProgresoJuegoViewSet, basename='progreso-juego')
router.register(r'qr', QRViewSet)
router.register(r'nfc', NFCViewSet, basename='nfc')

# URLs de la API
urlpatterns = [
    # Autenticación JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # dj-rest-auth endpoints
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    # API endpoints principales
    path('', include(router.urls)),
    # Endpoint para productos únicos NFC no asignados
    path('productos-unicos-nfc/',
         __import__('apps.api_movil.views_productos_unicos_nfc').api_movil.views_productos_unicos_nfc.productos_unicos_nfc,
         name='productos_unicos_nfc'),
]