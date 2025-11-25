from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel, EstadoChoices


class Wallet(BaseModel):
    """
    Wallets de usuarios basado en tabla wallet del script.sql
    """
    TIPO_WALLET_CHOICES = [
        ('custodial', 'Custodial'),
        ('externo', 'Externo'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wallets',
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    direccion = models.CharField(max_length=100, unique=True, verbose_name='Dirección')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_WALLET_CHOICES,
        verbose_name='Tipo'
    )
    proveedor = models.CharField(max_length=50, blank=True, verbose_name='Proveedor')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('suspendido', 'Suspendido'),
        ],
        default='activo',
        verbose_name='Estado'
    )
    
    # Campos adicionales
    red_blockchain = models.CharField(max_length=50, default='ethereum', verbose_name='Red blockchain')
    balance_cache = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        default=0, 
        verbose_name='Balance en cache'
    )
    ultima_sincronizacion = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='Última sincronización'
    )
    
    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        db_table = 'wallet'
    
    def __str__(self):
        usuario_str = self.usuario.email if self.usuario else 'Sin usuario'
        return f"Wallet {self.direccion[:10]}... - {usuario_str}"
    
    @property
    def direccion_corta(self):
        """Retorna una versión corta de la dirección"""
        return f"{self.direccion[:6]}...{self.direccion[-4:]}"


class NFT(BaseModel):
    """
    NFTs del sistema basado en tabla nft del script.sql
    """
    MINT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('minted', 'Minteado'),
        ('failed', 'Fallido'),
    ]
    
    ESTADO_NFT_CHOICES = [
        ('activo', 'Activo'),
        ('transferido', 'Transferido'),
        ('quemado', 'Quemado'),
    ]
    
    producto = models.ForeignKey(
        'productos.Producto', 
        on_delete=models.CASCADE, 
        related_name='nfts',
        verbose_name='Producto'
    )
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='nfts',
        verbose_name='Wallet'
    )
    token_id = models.CharField(max_length=100, blank=True, verbose_name='Token ID')
    contract_address = models.CharField(max_length=100, blank=True, verbose_name='Dirección del contrato')
    metadata_uri = models.CharField(max_length=255, blank=True, verbose_name='URI de metadatos')
    mint_status = models.CharField(
        max_length=20,
        choices=MINT_STATUS_CHOICES,
        default='pending',
        verbose_name='Estado de minteo'
    )
    mint_tx_hash = models.CharField(max_length=100, blank=True, verbose_name='Hash de transacción de mint')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_NFT_CHOICES,
        default='activo',
        verbose_name='Estado'
    )
    
    # Campos adicionales
    nombre = models.CharField(max_length=200, verbose_name='Nombre del NFT')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    imagen_url = models.URLField(blank=True, verbose_name='URL de imagen')
    atributos = models.JSONField(default=dict, blank=True, verbose_name='Atributos del NFT')
    precio_mint = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        verbose_name='Precio de minteo'
    )
    royalty_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        verbose_name='Porcentaje de regalías'
    )
    
    class Meta:
        verbose_name = 'NFT'
        verbose_name_plural = 'NFTs'
        db_table = 'nft'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"NFT {self.nombre} - Token ID: {self.token_id or 'Pendiente'}"
    
    @property
    def esta_minteado(self):
        """Verifica si el NFT ya fue minteado"""
        return self.mint_status == 'minted'
    
    @property
    def propietario_actual(self):
        """Retorna el propietario actual del NFT"""
        return self.wallet.usuario if self.wallet else None


class NFTTransaccion(BaseModel):
    """
    Transacciones de NFTs basado en tabla nft_transaccion del script.sql
    """
    TIPO_TRANSACCION_CHOICES = [
        ('mint', 'Mint'),
        ('transfer', 'Transferencia'),
        ('burn', 'Quemado'),
        ('sale', 'Venta'),
    ]
    
    nft = models.ForeignKey(
        NFT, 
        on_delete=models.CASCADE, 
        related_name='transacciones',
        verbose_name='NFT'
    )
    wallet_from = models.ForeignKey(
        Wallet, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transacciones_enviadas',
        verbose_name='Wallet origen'
    )
    wallet_to = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='transacciones_recibidas',
        verbose_name='Wallet destino'
    )
    tx_hash = models.CharField(max_length=100, blank=True, verbose_name='Hash de transacción')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_TRANSACCION_CHOICES,
        verbose_name='Tipo de transacción'
    )
    monto = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        verbose_name='Monto'
    )
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha')
    
    # Campos adicionales
    gas_usado = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        verbose_name='Gas usado'
    )
    precio_gas = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        verbose_name='Precio del gas'
    )
    confirmada = models.BooleanField(default=False, verbose_name='Confirmada en blockchain')
    
    class Meta:
        verbose_name = 'Transacción NFT'
        verbose_name_plural = 'Transacciones NFT'
        db_table = 'nft_transaccion'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tipo} - NFT {self.nft.nombre} - {self.fecha.strftime('%Y-%m-%d')}"


class NFTClaimRequest(BaseModel):
    """
    Solicitudes de claim de NFTs basado en tabla nft_claim_request del script.sql
    """
    ESTADO_CLAIM_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('rechazado', 'Rechazado'),
    ]
    
    nft = models.ForeignKey(
        NFT, 
        on_delete=models.CASCADE, 
        related_name='claim_requests',
        verbose_name='NFT'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='claim_requests',
        verbose_name='Usuario'
    )
    direccion_destino = models.CharField(max_length=100, verbose_name='Dirección destino')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CLAIM_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    tx_hash = models.CharField(max_length=100, blank=True, verbose_name='Hash de transacción')
    fecha_solicitud = models.DateTimeField(default=timezone.now, verbose_name='Fecha de solicitud')
    
    # Campos adicionales
    fecha_procesado = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de procesado')
    razon_rechazo = models.TextField(blank=True, verbose_name='Razón de rechazo')
    gas_estimado = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        verbose_name='Gas estimado'
    )
    
    class Meta:
        verbose_name = 'Solicitud de Claim NFT'
        verbose_name_plural = 'Solicitudes de Claim NFT'
        db_table = 'nft_claim_request'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Claim request de {self.usuario.email} para NFT {self.nft.nombre}"
    
    def aprobar_claim(self, tx_hash):
        """Aprueba la solicitud de claim"""
        self.estado = 'completado'
        self.tx_hash = tx_hash
        self.fecha_procesado = timezone.now()
        self.save()
    
    def rechazar_claim(self, razon):
        """Rechaza la solicitud de claim"""
        self.estado = 'rechazado'
        self.razon_rechazo = razon
        self.fecha_procesado = timezone.now()
        self.save()


# Modelo adicional para colecciones de NFTs
class ColeccionNFT(BaseModel):
    """
    Colecciones de NFTs para organizar y categorizar
    """
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='colecciones_creadas'
    )
    imagen_portada = models.ImageField(upload_to='colecciones/', blank=True, verbose_name='Imagen de portada')
    contract_address = models.CharField(max_length=100, blank=True, verbose_name='Dirección del contrato')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        verbose_name = 'Colección NFT'
        verbose_name_plural = 'Colecciones NFT'
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_nfts(self):
        """Retorna el total de NFTs en la colección"""
        return self.nfts.count()


# Relación many-to-many entre NFT y Colección
class NFTColeccion(BaseModel):
    """
    Relación entre NFTs y colecciones
    """
    nft = models.ForeignKey(NFT, on_delete=models.CASCADE, related_name='colecciones')
    coleccion = models.ForeignKey(ColeccionNFT, on_delete=models.CASCADE, related_name='nfts')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden en la colección')
    
    class Meta:
        verbose_name = 'NFT en Colección'
        verbose_name_plural = 'NFTs en Colección'
        unique_together = ['nft', 'coleccion']
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.nft.nombre} en {self.coleccion.nombre}"