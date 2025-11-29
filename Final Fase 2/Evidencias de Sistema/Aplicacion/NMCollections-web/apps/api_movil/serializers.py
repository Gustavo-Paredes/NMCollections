from rest_framework import serializers

class NFCCrearSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(required=True)
from apps.core.models import NFC
class NFCConsultaSerializer(serializers.ModelSerializer):
    producto = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()
    imagen = serializers.SerializerMethodField()
    es_dueno = serializers.SerializerMethodField()

    class Meta:
        model = NFC
        fields = ['codigo_nfc', 'estado', 'fecha_asignacion', 'producto', 'usuario', 'imagen', 'es_dueno']

    def get_producto(self, obj):
        return {
            'id': obj.producto.id,
            'nombre': obj.producto.nombre,
            'descripcion': obj.producto.descripcion
        }

    def get_usuario(self, obj):
        if obj.usuario is None:
            return None
        return {
            'id': obj.usuario.id,
            'username': obj.usuario.username
        }

    def get_imagen(self, obj):
        # Buscar imagen principal en ImagenProducto
        imagen_principal = obj.producto.imagenes.filter(es_principal=True).first()
        if imagen_principal and imagen_principal.imagen:
            return imagen_principal.imagen.url
        # Si no hay imagen principal, usar imagen_referencia
        if obj.producto.imagen_referencia:
            return obj.producto.imagen_referencia.url
        return None

    def get_es_dueno(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.usuario == request.user
        return False
"""
Serializers centralizados para toda la API del sistema
Importa y expone serializers de todas las apps sin duplicar lógica
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# Importar modelos de todas las apps
from apps.usuarios.models import Usuario, Rol, PerfilUsuario
from apps.productos.models import CategoriaProducto, Producto, ProductoPersonalizacion, ImagenProducto, ResenaProducto
from apps.carrito.models import Carrito, CarritoProducto, ListaDeseos
from apps.pedidos.models import Pedido, PedidoProducto, HistorialEstadoPedido
from apps.pagos.models import TransaccionPago, MetodoPago, TarjetaUsuario
from apps.subastas.models import Subasta, Puja, NotificacionSubasta
# from apps.nft.models import Wallet, NFT, NFTTransaccion, NFTClaimRequest, ColeccionNFT  # App eliminada
from apps.juegos.models import MiniJuego, Partida, ProgresoJuego, Logro
from apps.core.models import QR, NFC, Configuracion


# ========================================
# SERIALIZERS DE USUARIOS
# ========================================

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'correo', 'username', 'password', 'password_confirm',
            'nombre', 'apellido_paterno', 'apellido_materno',
            'telefono', 'direccion', 'rol'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user



class UsuarioDetalleSerializer(serializers.ModelSerializer):
    """Serializer para detalles del usuario autenticado"""
    rol = RolSerializer(read_only=True)
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = Usuario
        fields = [
            'id', 'correo', 'username', 'nombre', 'apellido_paterno', 
            'apellido_materno', 'telefono', 'direccion', 'rol',
            'fecha_registro', 'estado', 'nombre_completo'
        ]
        read_only_fields = ['id', 'fecha_registro', 'estado']

# Serializer mínimo para NFC
class UsuarioMinimoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'correo', 'nombre_completo']


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = '__all__'


# ========================================
# SERIALIZERS DE PRODUCTOS
# ========================================

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion']


class ProductoPersonalizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoPersonalizacion
        fields = ['id', 'opcion_tipo', 'valor', 'preview_url']


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'imagen', 'alt_text', 'es_principal', 'orden']


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer para lista de productos (menos campos)"""
    categoria = CategoriaProductoSerializer(read_only=True)
    imagen_principal = serializers.SerializerMethodField()
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio_base', 'stock', 'tipo',
            'categoria', 'estado', 'disponible', 'imagen_principal', 'imagenes'
        ]
    
    def get_imagen_principal(self, obj):
        imagen = obj.imagenes.filter(es_principal=True).first()
        if not imagen:
            imagen = obj.imagenes.first()
        if imagen:
            return ImagenProductoSerializer(imagen).data
        # Fallback: usar imagen_referencia si existe
        if obj.imagen_referencia:
            return {
                'imagen': obj.imagen_referencia.url,
                'alt_text': 'Imagen de referencia',
                'es_principal': True,
                'orden': 0
            }
        return None


class ProductoDetalleSerializer(serializers.ModelSerializer):
    """Serializer para detalle completo del producto"""
    categoria = CategoriaProductoSerializer(read_only=True)
    personalizaciones = ProductoPersonalizacionSerializer(many=True, read_only=True)
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    promedio_calificacion = serializers.SerializerMethodField()
    total_resenas = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio_base', 'stock', 'tipo',
            'categoria', 'estado', 'disponible', 'fecha_creacion',
            'personalizaciones', 'imagenes', 'promedio_calificacion', 'total_resenas'
        ]
    
    def get_promedio_calificacion(self, obj):
        resenas = obj.resenas.all()
        if resenas:
            return sum(r.calificacion for r in resenas) / len(resenas)
        return 0
    
    def get_total_resenas(self, obj):
        return obj.resenas.count()


class ResenaProductoSerializer(serializers.ModelSerializer):
    usuario = UsuarioDetalleSerializer(read_only=True)
    
    class Meta:
        model = ResenaProducto
        fields = ['id', 'usuario', 'calificacion', 'titulo', 'comentario', 'compra_verificada', 'created_at']


# ========================================
# SERIALIZERS DE CARRITO
# ========================================

class CarritoProductoSerializer(serializers.ModelSerializer):
    producto = ProductoListSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CarritoProducto
        fields = ['id', 'producto', 'cantidad', 'precio_unitario', 'personalizacion', 'subtotal']


class CarritoSerializer(serializers.ModelSerializer):
    productos = CarritoProductoSerializer(many=True, read_only=True)
    total_productos = serializers.ReadOnlyField()
    total_precio = serializers.ReadOnlyField()
    
    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'estado', 'fecha_creacion', 'productos', 'total_productos', 'total_precio']


# ========================================
# SERIALIZERS DE PEDIDOS
# ========================================

class PedidoProductoSerializer(serializers.ModelSerializer):
    producto = ProductoListSerializer(read_only=True)
    
    class Meta:
        model = PedidoProducto
        fields = ['id', 'producto', 'cantidad', 'personalizacion', 'precio_total']


class PedidoSerializer(serializers.ModelSerializer):
    productos = PedidoProductoSerializer(many=True, read_only=True)
    usuario = UsuarioDetalleSerializer(read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'numero_pedido', 'usuario', 'fecha_pedido', 'estado',
            'total', 'metodo_pago', 'direccion_envio', 'notas',
            'numero_seguimiento', 'productos'
        ]


# ========================================
# SERIALIZERS DE PAGOS
# ========================================

class TransaccionPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionPago
        fields = [
            'id', 'pedido', 'fecha_transaccion', 'monto', 'metodo_pago',
            'estado', 'codigo_autorizacion', 'es_exitosa'
        ]


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id', 'nombre', 'tipo', 'descripcion', 'activo']


# ========================================
# SERIALIZERS DE SUBASTAS
# ========================================

class PujaSerializer(serializers.ModelSerializer):
    usuario = UsuarioDetalleSerializer(read_only=True)
    
    class Meta:
        model = Puja
        fields = ['id', 'usuario', 'monto', 'fecha', 'activa']


class SubastaSerializer(serializers.ModelSerializer):
    producto = ProductoListSerializer(read_only=True)
    ganador = UsuarioDetalleSerializer(read_only=True)
    precio_actual = serializers.ReadOnlyField()
    total_pujas = serializers.ReadOnlyField()
    ultima_puja = serializers.SerializerMethodField()
    
    class Meta:
        model = Subasta
        fields = [
            'id', 'producto', 'fecha_inicio', 'fecha_fin', 'precio_inicial',
            'estado', 'ganador', 'precio_actual', 'total_pujas',
            'esta_activa', 'ultima_puja'
        ]
    
    def get_ultima_puja(self, obj):
        ultima = obj.pujas.order_by('-fecha').first()
        return PujaSerializer(ultima).data if ultima else None


# ========================================
# SERIALIZERS DE NFT - COMENTADOS (App eliminada)
# ========================================

# class WalletSerializer(serializers.ModelSerializer):
#     direccion_corta = serializers.ReadOnlyField()
#     
#     class Meta:
#         model = Wallet
#         fields = ['id', 'direccion', 'direccion_corta', 'tipo', 'red_blockchain', 'estado']


# class NFTSerializer(serializers.ModelSerializer):
#     producto = ProductoListSerializer(read_only=True)
#     wallet = WalletSerializer(read_only=True)
#     propietario_actual = serializers.ReadOnlyField()
#     
#     class Meta:
#         model = NFT
#         fields = [
#             'id', 'producto', 'wallet', 'nombre', 'descripcion', 'token_id',
#             'contract_address', 'mint_status', 'estado', 'esta_minteado',
#             'propietario_actual', 'atributos'
#         ]


# ========================================
# SERIALIZERS DE JUEGOS
# ========================================

class MiniJuegoSerializer(serializers.ModelSerializer):
    total_partidas = serializers.ReadOnlyField()
    jugadores_unicos = serializers.ReadOnlyField()
    
    class Meta:
        model = MiniJuego
        fields = [
            'id', 'nombre', 'tipo', 'descripcion', 'activo',
            'imagen_icono', 'total_partidas', 'jugadores_unicos'
        ]


class PartidaSerializer(serializers.ModelSerializer):
    juego = MiniJuegoSerializer(read_only=True)
    player1 = UsuarioDetalleSerializer(read_only=True)
    player2 = UsuarioDetalleSerializer(read_only=True)
    ganador = UsuarioDetalleSerializer(read_only=True)
    
    class Meta:
        model = Partida
        fields = [
            'id', 'juego', 'player1', 'player2', 'ganador', 'resultado',
            'fecha_inicio', 'fecha_fin', 'puntaje_player1', 'puntaje_player2',
            'esta_en_curso', 'duracion_segundos'
        ]


class ProgresoJuegoSerializer(serializers.ModelSerializer):
    juego = MiniJuegoSerializer(read_only=True)
    usuario = UsuarioDetalleSerializer(read_only=True)
    porcentaje_victoria = serializers.ReadOnlyField()
    
    class Meta:
        model = ProgresoJuego
        fields = [
            'id', 'juego', 'usuario', 'nivel', 'puntaje_total',
            'partidas_jugadas', 'partidas_ganadas', 'mejor_puntaje',
            'porcentaje_victoria', 'logros'
        ]


# ========================================
# SERIALIZERS DE CORE (QR/NFC)
# ========================================

class QRSerializer(serializers.ModelSerializer):
    producto = ProductoListSerializer(read_only=True)
    
    class Meta:
        model = QR
        fields = ['id', 'producto', 'codigo_qr', 'url_redireccion', 'estado', 'fecha_generacion']



class NFCSerializer(serializers.ModelSerializer):
    producto = ProductoListSerializer(read_only=True)
    usuario = UsuarioMinimoSerializer(read_only=True)
    class Meta:
        model = NFC
        fields = ['id', 'producto', 'usuario', 'codigo_nfc', 'estado', 'fecha_asignacion']