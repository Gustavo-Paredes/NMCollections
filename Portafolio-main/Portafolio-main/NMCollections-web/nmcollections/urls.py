"""
URL configuration for nmcollections project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.core import views as core_views

# Configuración de Swagger para documentación de API
schema_view = get_schema_view(
    openapi.Info(
        title="NM Collections API",
        default_version='v1',
        description="API completa para plataforma de e-commerce + juegos + subastas + NFT",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@nmcollections.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Documentation (Swagger)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Página principal y vistas web
    path('', include('apps.core.urls')),
    
    # URLs de usuarios (AÑADIR ESTA LÍNEA)
    path('usuarios/', include('apps.usuarios.urls')),

    path('pedidos/', include('apps.pedidos.urls')),
    path('api/v1/pedidos/', include('apps.pedidos.urls')),
    
    # URLs de carrito de compras
    path('carrito/', include('apps.carrito.urls')),
    
    # URLs de pagos (WebPay y otros métodos de pago)
    path('pagos/', include('apps.pagos.urls')),

    path('subastas/', include('apps.subastas.urls')),

    # URLs de productos
    path('productos/', include('apps.productos.urls')),

    # URLs de personalización - Canvas Editor
    path('personalizacion/', include('apps.personalizacion.urls')),
    # Chat de soporte
    path('soporte/', include('apps.soporte.urls')),
    
    # API Principal
    path('api/v1/', include('apps.api_movil.urls')),
    
    # API browsable (DRF)
    path('api-auth/', include('rest_framework.urls')),

    path('NFC/<codigo_nfc>/', core_views.nfc_detail, name='nfc_detail'),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
