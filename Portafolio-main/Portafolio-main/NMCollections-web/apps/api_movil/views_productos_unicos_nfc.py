

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from apps.productos.models import Producto, CategoriaProducto
from apps.core.models import NFC
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model

@swagger_auto_schema(
    method='get',
    operation_description="Lista productos con categoría 'Carta única - NFC' que no tienen NFC asignado.",
    responses={
        200: openapi.Response(
            description="Lista de productos disponibles para asignar NFC",
            examples={
                "application/json": [
                    {"id": 1, "nombre": "Carta Ejemplo"},
                    {"id": 2, "nombre": "Carta Ejemplo 2"}
                ]
            }
        ),
        404: openapi.Response(description="No existe la categoría 'Carta única - NFC'")
    }
)
@api_view(['GET'])
def productos_unicos_nfc(request):
    user = request.user
    # Permitir solo admin o diseñador (rol id=5)
    if not (user.is_staff or getattr(getattr(user, 'rol', None), 'id', None) == 5):
        return Response({'detail': 'No tienes permiso para realizar esta acción.'}, status=403)
    # Buscar la categoría "Carta única - NFC"
    categoria = CategoriaProducto.objects.filter(nombre__iexact="Carta unica - NFC").first()
    if not categoria:
        return Response({"error": "No existe la categoría 'Carta única - NFC'"}, status=404)
    # Productos de esa categoría que NO están en la tabla NFC
    productos = Producto.objects.filter(categoria=categoria).exclude(id__in=NFC.objects.values_list('producto_id', flat=True))
    # Serializar solo id y nombre
    data = [{"id": p.id, "nombre": p.nombre} for p in productos]
    return Response(data)
