"""
Servicio de recorte inteligente de imágenes
Utiliza AI para remover fondos y extraer figuras de jugadores
"""
import os
import io
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from rembg import remove
import cv2
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings


class RecorteInteligenteService:
    """
    Servicio para realizar recortes inteligentes de imágenes
    """
    
    @staticmethod
    def remover_fondo(imagen_path):
        """
        Remueve el fondo de una imagen usando AI
        
        Args:
            imagen_path: Ruta a la imagen original
            
        Returns:
            tuple: (imagen_sin_fondo_pil, imagen_bytes)
        """
        try:
            # Leer la imagen
            with open(imagen_path, 'rb') as f:
                input_data = f.read()
            
            # Remover fondo usando rembg (AI)
            output_data = remove(input_data)
            
            # Convertir a PIL Image
            imagen_sin_fondo = Image.open(io.BytesIO(output_data))
            
            return imagen_sin_fondo, output_data
            
        except Exception as e:
            print(f"Error removiendo fondo: {str(e)}")
            return None, None
    
    @staticmethod
    def mejorar_recorte(imagen_pil):
        """
        Mejora el recorte aplicando filtros y optimizaciones
        
        Args:
            imagen_pil: Imagen PIL con fondo removido
            
        Returns:
            PIL.Image: Imagen mejorada
        """
        try:
            # Convertir a RGBA si no lo está
            if imagen_pil.mode != 'RGBA':
                imagen_pil = imagen_pil.convert('RGBA')
            
            # Mejorar contraste
            enhancer = ImageEnhance.Contrast(imagen_pil)
            imagen_pil = enhancer.enhance(1.2)
            
            # Mejorar nitidez
            imagen_pil = imagen_pil.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
            
            # Limpiar bordes
            imagen_pil = RecorteInteligenteService._limpiar_bordes(imagen_pil)
            
            return imagen_pil
            
        except Exception as e:
            print(f"Error mejorando recorte: {str(e)}")
            return imagen_pil
    
    @staticmethod
    def _limpiar_bordes(imagen_pil):
        """
        Limpia bordes irregulares del recorte
        """
        try:
            # Convertir a array numpy
            img_array = np.array(imagen_pil)
            
            # Obtener canal alpha
            alpha = img_array[:, :, 3]
            
            # Encontrar contornos
            contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Obtener el contorno más grande (debería ser el jugador)
                contorno_principal = max(contours, key=cv2.contourArea)
                
                # Crear máscara suavizada
                mask = np.zeros_like(alpha)
                cv2.fillPoly(mask, [contorno_principal], 255)
                
                # Aplicar desenfoque gaussiano para suavizar bordes
                mask = cv2.GaussianBlur(mask, (5, 5), 0)
                
                # Aplicar la máscara mejorada
                img_array[:, :, 3] = mask
                
                return Image.fromarray(img_array)
            
            return imagen_pil
            
        except Exception as e:
            print(f"Error limpiando bordes: {str(e)}")
            return imagen_pil
    
    @staticmethod
    def recortar_y_centrar(imagen_pil, ancho_objetivo=400, alto_objetivo=450):
        """
        Recorta y centra la figura del jugador en las dimensiones objetivo
        
        Args:
            imagen_pil: Imagen PIL con fondo removido
            ancho_objetivo: Ancho deseado en pixels
            alto_objetivo: Alto deseado en pixels
            
        Returns:
            PIL.Image: Imagen recortada y centrada
        """
        try:
            # Encontrar bounding box del contenido
            bbox = imagen_pil.getbbox()
            
            if bbox:
                # Recortar al contenido
                imagen_recortada = imagen_pil.crop(bbox)
                
                # Calcular escalado manteniendo proporción
                ancho_actual, alto_actual = imagen_recortada.size
                escala_x = ancho_objetivo / ancho_actual
                escala_y = alto_objetivo / alto_actual
                escala = min(escala_x, escala_y) * 0.9  # 90% para dejar margen
                
                # Redimensionar
                nuevo_ancho = int(ancho_actual * escala)
                nuevo_alto = int(alto_actual * escala)
                imagen_escalada = imagen_recortada.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
                
                # Crear canvas transparente
                canvas = Image.new('RGBA', (ancho_objetivo, alto_objetivo), (0, 0, 0, 0))
                
                # Centrar la imagen
                x_offset = (ancho_objetivo - nuevo_ancho) // 2
                y_offset = (alto_objetivo - nuevo_alto) // 2
                canvas.paste(imagen_escalada, (x_offset, y_offset), imagen_escalada)
                
                return canvas
            
            return imagen_pil
            
        except Exception as e:
            print(f"Error recortando y centrando: {str(e)}")
            return imagen_pil
    
    @staticmethod
    def procesar_imagen_completa(imagen_path, ancho_objetivo=400, alto_objetivo=450):
        """
        Proceso completo: remover fondo, mejorar, recortar y centrar
        
        Args:
            imagen_path: Ruta a la imagen original
            ancho_objetivo: Ancho deseado
            alto_objetivo: Alto deseado
            
        Returns:
            tuple: (imagen_procesada_pil, imagen_bytes)
        """
        try:
            print(f"🔄 Procesando imagen: {imagen_path}")
            
            # Paso 1: Remover fondo
            print("   🎯 Removiendo fondo...")
            imagen_sin_fondo, _ = RecorteInteligenteService.remover_fondo(imagen_path)
            
            if imagen_sin_fondo is None:
                return None, None
            
            # Paso 2: Mejorar recorte
            print("   ✨ Mejorando recorte...")
            imagen_mejorada = RecorteInteligenteService.mejorar_recorte(imagen_sin_fondo)
            
            # Paso 3: Recortar y centrar
            print("   📐 Recortando y centrando...")
            imagen_final = RecorteInteligenteService.recortar_y_centrar(
                imagen_mejorada, ancho_objetivo, alto_objetivo
            )
            
            # Convertir a bytes
            output_buffer = io.BytesIO()
            imagen_final.save(output_buffer, format='PNG', optimize=True)
            imagen_bytes = output_buffer.getvalue()
            
            print("   ✅ Procesamiento completado")
            return imagen_final, imagen_bytes
            
        except Exception as e:
            print(f"❌ Error en procesamiento completo: {str(e)}")
            return None, None
    
    @staticmethod
    def guardar_imagen_procesada(imagen_bytes, nombre_archivo):
        """
        Guarda la imagen procesada en el storage de Django
        
        Args:
            imagen_bytes: Bytes de la imagen procesada
            nombre_archivo: Nombre del archivo
            
        Returns:
            str: Ruta del archivo guardado
        """
        try:
            # Crear ruta para imágenes procesadas
            ruta_relativa = f'images/procesadas/{nombre_archivo}'
            
            # Guardar usando Django storage
            path = default_storage.save(ruta_relativa, ContentFile(imagen_bytes))
            
            return path
            
        except Exception as e:
            print(f"Error guardando imagen: {str(e)}")
            return None


class RecorteUtils:
    """
    Utilidades adicionales para el recorte inteligente
    """
    
    @staticmethod
    def es_imagen_valida(archivo):
        """
        Verifica si el archivo es una imagen válida
        """
        extensiones_validas = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        nombre_archivo = archivo.name.lower()
        
        return any(nombre_archivo.endswith(ext) for ext in extensiones_validas)
    
    @staticmethod
    def obtener_dimensiones_recomendadas(tipo_elemento):
        """
        Obtiene las dimensiones recomendadas según el tipo de elemento
        """
        dimensiones = {
            'foto_jugador': (400, 450),
            'logo_equipo': (100, 100),
            'bandera_pais': (60, 40),
            'firma_jugador': (200, 80),
        }
        
        return dimensiones.get(tipo_elemento, (400, 450))