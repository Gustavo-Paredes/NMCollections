from rest_framework import serializers
from .models import (
    Plantilla, PlantillaElemento, PlantillaFondo, 
    CartaPersonalizada, CartaParametro
)


class PlantillaElementoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantillaElemento
        fields = [
            'id', 'nombre_parametro', 'tipo_elemento', 'posicion_x', 
            'posicion_y', 'ancho', 'alto', 'fuente', 'color', 'z_index'
        ]


class PlantillaFondoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantillaFondo
        fields = ['id', 'tipo_fondo', 'valor']


class PlantillaSerializer(serializers.ModelSerializer):
    elementos = PlantillaElementoSerializer(
        source='plantillaelemento_set', 
        many=True, 
        read_only=True
    )
    fondos = PlantillaFondoSerializer(
        source='plantillafondo_set', 
        many=True, 
        read_only=True
    )
    usuario_creador_nombre = serializers.CharField(
        source='usuario_creador.first_name', 
        read_only=True
    )
    imagen_marco_url = serializers.SerializerMethodField()
    
    def get_imagen_marco_url(self, obj):
        """Obtener URL de la imagen del marco si existe"""
        if obj.imagen_marco:
            return obj.imagen_marco.url
        return None
    
    class Meta:
        model = Plantilla
        fields = [
            'id', 'nombre', 'descripcion', 'tipo_carta', 'imagen_preview', 
            'estado', 'usuario_creador', 'usuario_creador_nombre', 'fecha_creacion',
            'imagen_marco', 'imagen_marco_url', 'ancho_marco', 'alto_marco', 
            'diseñador', 'archivo_original', 'elementos', 'fondos'
        ]
        extra_kwargs = {
            'usuario_creador': {'write_only': True}
        }


class PlantillaCreateSerializer(serializers.ModelSerializer):
    elementos = PlantillaElementoSerializer(many=True, required=False)
    fondos = PlantillaFondoSerializer(many=True, required=False)
    
    class Meta:
        model = Plantilla
        fields = [
            'nombre', 'descripcion', 'tipo_carta', 'imagen_preview', 
            'estado', 'elementos', 'fondos'
        ]
    
    def create(self, validated_data):
        elementos_data = validated_data.pop('elementos', [])
        fondos_data = validated_data.pop('fondos', [])
        
        # Agregar usuario creador del request
        validated_data['usuario_creador'] = self.context['request'].user
        
        plantilla = Plantilla.objects.create(**validated_data)
        
        # Crear elementos
        for elemento_data in elementos_data:
            PlantillaElemento.objects.create(plantilla=plantilla, **elemento_data)
        
        # Crear fondos
        for fondo_data in fondos_data:
            PlantillaFondo.objects.create(plantilla=plantilla, **fondo_data)
        
        return plantilla


class CartaParametroSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaParametro
        fields = ['id', 'nombre_parametro', 'tipo_parametro', 'valor']


class CartaPersonalizadaSerializer(serializers.ModelSerializer):
    parametros = CartaParametroSerializer(
        source='cartaparametro_set', 
        many=True, 
        read_only=True
    )
    plantilla_info = PlantillaSerializer(source='plantilla', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.first_name', read_only=True)
    # Agregar campo ruta_imagen
    ruta_imagen = serializers.CharField(read_only=True)
    
    class Meta:
        model = CartaPersonalizada
        fields = [
            'id', 'usuario', 'usuario_nombre', 'plantilla', 'plantilla_info',
            'nombre_carta', 'estado', 'fecha_creacion', 'parametros', 'ruta_imagen'
        ]
        extra_kwargs = {
            'usuario': {'write_only': True},
            'plantilla': {'write_only': True}
        }


class CartaPersonalizadaCreateSerializer(serializers.ModelSerializer):
    parametros = CartaParametroSerializer(many=True, required=False)
    
    class Meta:
        model = CartaPersonalizada
        fields = ['plantilla', 'nombre_carta', 'parametros']
    
    def create(self, validated_data):
        parametros_data = validated_data.pop('parametros', [])
        
        # Agregar usuario del request
        validated_data['usuario'] = self.context['request'].user
        
        carta = CartaPersonalizada.objects.create(**validated_data)
        
        # Crear parámetros
        for parametro_data in parametros_data:
            CartaParametro.objects.create(carta=carta, **parametro_data)
        
        return carta


class CartaPersonalizadaUpdateSerializer(serializers.ModelSerializer):
    parametros = CartaParametroSerializer(many=True, required=False)
    
    class Meta:
        model = CartaPersonalizada
        fields = ['nombre_carta', 'estado', 'parametros']
    
    def update(self, instance, validated_data):
        parametros_data = validated_data.pop('parametros', None)
        
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar parámetros si se proporcionan
        if parametros_data is not None:
            # Eliminar parámetros existentes
            instance.cartaparametro_set.all().delete()
            
            # Crear nuevos parámetros
            for parametro_data in parametros_data:
                CartaParametro.objects.create(carta=instance, **parametro_data)
        
        return instance


# Serializers adicionales para casos específicos
class PlantillaMinimalSerializer(serializers.ModelSerializer):
    """Serializer mínimo para listados de plantillas"""
    class Meta:
        model = Plantilla
        fields = ['id', 'nombre', 'tipo_carta', 'imagen_preview', 'estado']


class CartaPersonalizadaMinimalSerializer(serializers.ModelSerializer):
    """Serializer mínimo para listados de cartas"""
    plantilla_nombre = serializers.CharField(source='plantilla.nombre', read_only=True)
    
    class Meta:
        model = CartaPersonalizada
        fields = ['id', 'nombre_carta', 'estado', 'fecha_creacion', 'plantilla_nombre']