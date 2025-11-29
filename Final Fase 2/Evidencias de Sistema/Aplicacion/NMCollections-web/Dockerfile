# Dockerfile optimizado para producción - NM Collections Trading Cards
# Usa Python 3.13 slim para optimizar tamaño
FROM python:3.13-slim-bullseye

# Configurar variables de entorno para producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    # Para Pillow y procesamiento de imágenes
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    # Para rembg y AI (onnxruntime)
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Para PostgreSQL
    libpq-dev \
    # Para compilación
    gcc \
    g++ \
    # Limpiar cache
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Crear usuario no-root para seguridad
RUN adduser --disabled-password --gecos '' appuser

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios necesarios con permisos apropiados
RUN mkdir -p /app/media/cartas \
             /app/media/plantillas/marcos \
             /app/media/images/procesadas \
             /app/staticfiles \
             /app/logs && \
    chown -R appuser:appuser /app

# Copiar código de la aplicación
COPY . .


# Cambiar a usuario no-root
USER appuser

# Exponer puerto para Django
EXPOSE 8000

# Comando de inicio optimizado para producción
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn nmcollections.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120"]