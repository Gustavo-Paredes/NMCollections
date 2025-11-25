from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pedido
from .permissions import IsAdminOrDesigner
from django.contrib.auth import get_user_model

class PedidoAllListAPIView(APIView):
    permission_classes = [IsAdminOrDesigner]

    def get(self, request, format=None):
        pedidos = Pedido.objects.all().select_related('usuario')
        data = []
        for pedido in pedidos:
            productos_data = []
            for prod in pedido.productos.all():
                productos_data.append({
                    'id': prod.id,
                    'producto': {
                        'id': prod.producto.id,
                        'nombre': prod.producto.nombre,
                        'precio_base': prod.producto.precio_base,
                    },
                    'cantidad': prod.cantidad,
                    'personalizacion': prod.personalizacion,
                    'precio_total': float(prod.precio_total) if prod.precio_total else None
                })
            data.append({
                'id': pedido.id,
                'numero_pedido': pedido.numero_pedido,
                'usuario': pedido.usuario.email,
                'estado': pedido.estado,
                'total': float(pedido.total) if pedido.total else None,
                'fecha_pedido': pedido.fecha_pedido,
                'direccion_envio': pedido.direccion_envio,
                'metodo_pago': pedido.metodo_pago,
                'notas': pedido.notas,
                'productos': productos_data
            })
        return Response(data, status=status.HTTP_200_OK)
