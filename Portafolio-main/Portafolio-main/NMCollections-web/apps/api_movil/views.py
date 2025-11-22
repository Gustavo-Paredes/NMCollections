from drf_yasg.utils import swagger_auto_schema
"""
Views centralizadas para toda la API del sistema
Maneja todos los endpoints sin duplicar lógica
"""

from rest_framework import viewsets, status, permissions
from django.db import models
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models

# Importar modelos y serializers
from .serializers import *
from apps.usuarios.models import Usuario, Rol, PerfilUsuario
from apps.productos.models import CategoriaProducto, Producto, ResenaProducto
from apps.carrito.models import Carrito, CarritoProducto, ListaDeseos
from apps.pedidos.models import Pedido, PedidoProducto
from apps.pagos.models import TransaccionPago, MetodoPago
from apps.subastas.models import Subasta, Puja
# from apps.nft.models import Wallet, NFT, NFTTransaccion  # App eliminada
from apps.juegos.models import MiniJuego, Partida, ProgresoJuego
from apps.core.models import QR, NFC
from apps.core.models import NFCLog


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ========================================
# VIEWSETS DE USUARIOS
# ========================================

class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioDetalleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['correo', 'nombre', 'apellido_paterno']
    filterset_fields = ['estado', 'rol']
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioRegistroSerializer
        return UsuarioDetalleSerializer
    
    @action(detail=False, methods=['get', 'patch'])
    def perfil(self, request):
        """Endpoint para ver/editar perfil del usuario autenticado"""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para roles (solo lectura)"""
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]


# ========================================
# VIEWSETS DE PRODUCTOS
# ========================================

class CategoriaProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para categorías de productos"""
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer
    permission_classes = [permissions.AllowAny]


class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para productos"""
    from django.db.models import Q
    queryset = Producto.objects.filter(
        Q(estado='activo') & ~Q(tipo='personalizado') & (Q(tipo='digital') | Q(stock__isnull=True) | Q(stock__gt=0))
    )
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['categoria', 'tipo', 'estado']
    ordering_fields = ['precio_base', 'fecha_creacion', 'nombre']
    ordering = ['-fecha_creacion']
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetalleSerializer
        return ProductoListSerializer
    
    @action(detail=True, methods=['get'])
    def resenas(self, request, pk=None):
        """Obtener reseñas de un producto"""
        producto = self.get_object()
        resenas = producto.resenas.all().order_by('-created_at')
        page = self.paginate_queryset(resenas)
        if page is not None:
            serializer = ResenaProductoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ResenaProductoSerializer(resenas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def crear_resena(self, request, pk=None):
        """Crear reseña para un producto"""
        producto = self.get_object()
        data = request.data.copy()
        data['producto'] = producto.id
        data['usuario'] = request.user.id
        
        serializer = ResenaProductoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========================================
# VIEWSETS DE CARRITO
# ========================================

class CarritoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión del carrito"""
    serializer_class = CarritoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Carrito.objects.filter(usuario=self.request.user, estado='activo')
    
    @action(detail=False, methods=['get'])
    def actual(self, request):
        """Obtener carrito actual del usuario"""
        carrito, created = Carrito.objects.get_or_create(
            usuario=request.user,
            estado='activo',
            defaults={'fecha_creacion': timezone.now()}
        )
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_producto(self, request, pk=None):
        """Agregar producto al carrito"""
        carrito = self.get_object()
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad', 1)
        personalizacion = request.data.get('personalizacion', {})
        
        try:
            producto = Producto.objects.get(id=producto_id, estado='activo')
            carrito_producto, created = CarritoProducto.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={
                    'cantidad': cantidad,
                    'precio_unitario': producto.precio_base,
                    'personalizacion': personalizacion
                }
            )
            
            if not created:
                carrito_producto.cantidad += cantidad
                carrito_producto.save()
            
            return Response({'mensaje': 'Producto agregado al carrito'}, status=status.HTTP_201_CREATED)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# ========================================
# VIEWSETS DE PEDIDOS
# ========================================

class PedidoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pedidos"""
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado']
    ordering = ['-fecha_pedido']
    
    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['post'])
    def crear_desde_carrito(self, request):
        """Crear pedido desde carrito actual"""
        try:
            carrito = Carrito.objects.get(usuario=request.user, estado='activo')
            if not carrito.productos.exists():
                return Response({'error': 'El carrito está vacío'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                total=carrito.total_precio,
                direccion_envio=request.data.get('direccion_envio', ''),
                notas=request.data.get('notas', '')
            )
            
            # Copiar productos del carrito al pedido
            for carrito_producto in carrito.productos.all():
                PedidoProducto.objects.create(
                    pedido=pedido,
                    producto=carrito_producto.producto,
                    cantidad=carrito_producto.cantidad,
                    personalizacion=carrito_producto.personalizacion,
                    precio_total=carrito_producto.subtotal
                )
            
            # Finalizar carrito
            serializer_class = NFCConsultaSerializer
            carrito.save()
            
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Carrito.DoesNotExist:
            return Response({'error': 'No hay carrito activo'}, status=status.HTTP_404_NOT_FOUND)


# ========================================
# VIEWSETS DE SUBASTAS
# ========================================

class SubastaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para subastas"""
    queryset = Subasta.objects.all()
    serializer_class = SubastaSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado']
    ordering = ['-fecha_inicio']
    permission_classes = [permissions.AllowAny]
    
    @action(detail=True, methods=['get'])
    def pujas(self, request, pk=None):
        """Obtener pujas de una subasta"""
        subasta = self.get_object()
        pujas = subasta.pujas.all().order_by('-fecha')
        
        try:
            monto = float(monto)
            puede_pujar, mensaje = subasta.puede_pujar(request.user, monto)
            
            if not puede_pujar:
                return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
            
            puja = Puja.objects.create(
                subasta=subasta,
                usuario=request.user,
                monto=monto,
                ip_origen=request.META.get('REMOTE_ADDR')
            )
            
            serializer = PujaSerializer(puja)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError:
            return Response({'error': 'Monto inválido'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========================================
# VIEWSETS DE NFT - COMENTADOS (App eliminada)
# ========================================

# class WalletViewSet(viewsets.ModelViewSet):
#     """ViewSet para wallets"""
#     serializer_class = WalletSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     
#     def get_queryset(self):
#         return Wallet.objects.filter(usuario=self.request.user)


# class NFTViewSet(viewsets.ReadOnlyModelViewSet):
#     """ViewSet para NFTs"""
#     serializer_class = NFTSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = StandardResultsSetPagination
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['mint_status', 'estado']
#     
#     def get_queryset(self):
#         return NFT.objects.filter(wallet__usuario=self.request.user)


# ========================================
# VIEWSETS DE JUEGOS
# ========================================

class MiniJuegoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para mini juegos"""
    queryset = MiniJuego.objects.filter(activo=True)
    serializer_class = MiniJuegoSerializer
    permission_classes = [permissions.AllowAny]


class PartidaViewSet(viewsets.ModelViewSet):
    """ViewSet para partidas"""
    serializer_class = PartidaSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['juego', 'resultado']
    ordering = ['-fecha_inicio']
    
    def get_queryset(self):
        user = self.request.user
        return Partida.objects.filter(
            models.Q(player1=user) | models.Q(player2=user)
        )


class ProgresoJuegoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para progreso en juegos"""
    serializer_class = ProgresoJuegoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['juego']
    
    def get_queryset(self):
        return ProgresoJuego.objects.filter(usuario=self.request.user)


# ========================================
# VIEWSETS DE CORE (QR/NFC)
# ========================================

class QRViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para códigos QR"""
    queryset = QR.objects.filter(estado='activo')
    serializer_class = QRSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'codigo_qr'
    
    @action(detail=True, methods=['post'])
    def escanear(self, request, codigo_qr=None):
        """Registrar escaneo de código QR"""
        qr = self.get_object()
        # Aquí se registraría el log del escaneo
        return Response({'mensaje': 'QR escaneado correctamente', 'url': qr.url_redireccion})


class NFCViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NFCConsultaSerializer
    lookup_field = 'codigo_nfc'

    def retrieve(self, request, codigo_nfc=None):
        nfc = get_object_or_404(NFC, codigo_nfc=codigo_nfc)
        user = request.user
        # Si la carta está en transferencia y el usuario no es el dueño, transfiere la propiedad
        if nfc.estado == 'en_transferencia' and nfc.usuario != user and user.is_authenticated:
            nfc.usuario = user
            nfc.estado = 'activo'
            nfc.fecha_asignacion = timezone.now()
            nfc.save()
            NFCLog.objects.create(
                nfc=nfc,
                usuario=user,
                accion='transferencia_reclamada',
                fecha=timezone.now(),
                datos_adicionales={'detalle': 'Carta reclamada automáticamente por escaneo'}
            )
        serializer = NFCConsultaSerializer(nfc, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(request_body=NFCCrearSerializer, responses={201: NFCConsultaSerializer}, operation_description="Crear NFC solo requiere producto_id. El usuario queda sin asignar.")
    @action(detail=False, methods=['post'], url_path='crear', permission_classes=[permissions.IsAdminUser], serializer_class=NFCCrearSerializer)
    def crear(self, request):
        import random, string
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'error': 'Solo admin o staff pueden crear códigos NFC.'}, status=403)
        # Solo aceptar producto_id y usuario_id, ignorar otros campos
        data = request.data
        producto_id = data.get('producto_id')
        usuario_id = data.get('usuario_id')
        if not producto_id:
            return Response({'error': 'Falta producto_id.'}, status=400)
        # Generar código aleatorio siempre
        while True:
            codigo_nfc = 'NFC-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not NFC.objects.filter(codigo_nfc=codigo_nfc).exists():
                break
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no válido.'}, status=400)
        nfc = NFC.objects.create(
            usuario=None,
            producto=producto,
            codigo_nfc=codigo_nfc,
            estado='en_transferencia',
            fecha_asignacion=timezone.now()
        )
        # Log de creación
        NFCLog.objects.create(
            nfc=nfc,
            usuario=None,
            accion='registro',
            datos_adicionales={'detalle': 'Creación de NFC sin usuario'}
        )
        # Respuesta solo con los datos relevantes
        serializer = NFCConsultaSerializer(nfc)
        return Response(serializer.data, status=201)
        return Response(serializer.data)
        nfc = NFC.objects.create(
            usuario=usuario,
            producto=producto,
            codigo_nfc=codigo_nfc,
            estado='activo',
            fecha_asignacion=timezone.now()
        )
        NFCLog.objects.create(
            nfc=nfc,
            usuario=user,
            accion='registro',
            fecha=timezone.now(),
            datos_adicionales={'detalle': 'Creación de NFC por admin/staff'}
        )
        return Response({'success': True, 'id': nfc.id, 'codigo_nfc': nfc.codigo_nfc})

    @action(detail=True, methods=['post'], url_path='transferir', permission_classes=[permissions.IsAuthenticated])
    def transferir(self, request, codigo_nfc=None):
        nfc = get_object_or_404(NFC, codigo_nfc=codigo_nfc)
        if nfc.usuario != request.user:
            return Response({'error': 'Solo el dueño puede transferir la carta.'}, status=403)
        if nfc.estado != 'activo':
            return Response({'error': 'Solo cartas activas pueden ser transferidas.'}, status=400)
        nfc.estado = 'en_transferencia'
        nfc.save()
        # Registrar log
        NFCLog.objects.create(
            nfc=nfc,
            usuario=request.user,
            accion='transferencia_iniciada',
            fecha=timezone.now(),
            datos_adicionales={'detalle': 'Transferencia iniciada por dueño actual'}
        )
        return Response({'success': True, 'mensaje': 'Carta puesta en transferencia.'})


    serializer_class = NFCConsultaSerializer
    lookup_field = 'codigo_nfc'

    def get_permissions(self):
        # Permitir acceso público al retrieve, autenticación para el resto
        if self.action == 'retrieve':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Solo para list: NFCs del usuario autenticado y activos
        if self.action == 'list' and self.request.user.is_authenticated:
            return NFC.objects.filter(usuario=self.request.user, estado='activo')
        return NFC.objects.none()

