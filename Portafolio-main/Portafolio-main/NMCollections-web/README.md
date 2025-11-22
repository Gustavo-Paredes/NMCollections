# NM Collections - Plataforma E-commerce

Este repositorio contiene el código fuente de NM Collections, una plataforma de e-commerce desarrollada con Django que incluye funcionalidades para venta de productos personalizados, gestión de pedidos, pagos y personalización de cartas.

## 🚀 Despliegue rápido con Docker

La forma más fácil de ejecutar el proyecto es usando Docker:

```bash
# Descargar y ejecutar la imagen desde Docker Hub
docker run -d --name nmcollections -p 8004:8004 mpowo/nmcollections:latest

# Acceder a la aplicación
# http://localhost:8004
```

**¡Eso es todo!** La imagen incluye:
- ✅ Código actualizado desde GitHub
- ✅ Todas las dependencias Python
- ✅ Base de datos SQLite preconfigurada
- ✅ Usuarios completos creados automáticamente (admin, cliente, diseñador)

## 📋 Requisitos previos

### Para Docker (Recomendado)
- Docker Desktop instalado

### Para desarrollo local
- Python 3.13 o superior
- Git
- Pip (gestor de paquetes de Python)
- Un editor de código (VS Code, PyCharm, etc.)

## 🐳 Despliegue con Docker

### Usando imagen de Docker Hub (Recomendado)

```bash
# Ejecutar directamente desde Docker Hub
docker run -d --name nmcollections -p 8004:8004 mpowo/nmcollections:latest

# Verificar que esté corriendo
docker ps

# Ver logs si es necesario
docker logs nmcollections
```


## 💻 Desarrollo local (Sin Docker)

### 1. Clonar y configurar


```bash
git clone https://github.com/MatiasParada/Portafolio.git
cd Portafolio

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\Activate.ps1

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Inicializar base de datos

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python create_users.py  # Crea usuarios admin y cliente automáticamente
```

### 3. Ejecutar servidor

```bash
daphne -b 0.0.0.0 -p 8004 nmcollections.asgi:application
# Servidor de desarrollo - Puerto 8000
python manage.py runserver
```

## 🏗️ Arquitectura del proyecto

### Tecnologías principales
- **Backend**: Django 5.2.6
- **Base de datos**: SQLite (desarrollo), PostgreSQL (en proceso)
- **Containerización**: Docker con imagen optimizada
- **Frontend**: HTML, CSS, JavaScript

### Estructura del código

```
Portafolio/
├── apps/                      # Aplicaciones Django modularizadas
│   ├── api_movil/             # API REST para aplicaciones móviles
│   ├── carrito/               # Sistema de carrito de compras
│   ├── core/                  # Funcionalidad principal y vistas base
│   ├── juegos/                # (Eliminado: no disponible)
│   ├── nft/                   # (Eliminado: no disponible)
│   ├── pagos/                 # Procesamiento de pagos y transacciones
│   ├── pedidos/               # Gestión completa de pedidos
│   ├── personalizacion/       # Sistema de personalización de cartas
│   ├── productos/             # Catálogo y gestión de productos
│   ├── subastas/              # (Eliminado: no disponible)
│   └── usuarios/              # Autenticación y gestión de usuarios
├── nmcollections/             # Configuración del proyecto Django
│   ├── settings.py            # Configuraciones principales
│   ├── urls.py                # Rutas principales
│   ├── asgi.py                # Configuración ASGI para WebSockets
│   └── wsgi.py                # Configuración WSGI estándar
├── static/                    # Archivos estáticos (CSS, JS, imágenes)
├── staticfiles/               # Archivos estáticos recolectados
├── templates/                 # Plantillas HTML organizadas por app
├── media/                     # Archivos subidos por usuarios
├── Dockerfile                 # Configuración de contenedor Docker
├── docker-compose.yml         # Orquestación de servicios
├── requirements.txt           # Dependencias para desarrollo local
├── requirements-docker.txt    # Dependencias optimizadas para Docker
└── create_users.py            # Script de creación automática de usuarios
```

## 🔧 Características técnicas

### Docker Features
- **Build desde GitHub**: La imagen se construye automáticamente desde el repositorio
- **Usuario no-root**: Seguridad mejorada con usuario `appuser`
- **Puerto 8004**: Servidor Django optimizado
- **Auto-inicialización**: Migraciones y usuarios creados automáticamente

### Aplicación Features
- 🛒 **E-commerce completo** con carrito y pagos
- 🎨 **Personalización de cartas** con recortes inteligentes 
- 📱 **API móvil** con autenticación JWT (pronto)
- 🔐 **Sistema de usuarios** robusto 


## 👥 Usuarios del sistema


La aplicación crea automáticamente tres usuarios base:

| Usuario | Email | Password | Rol | Descripción |
|---------|--------|----------|-----|-------------|
| `admin` | admin@nmcollections.com | `admin123` | Administrador | Acceso completo al sistema |
| `cliente` | cliente@nmcollections.com | `cliente123` | Cliente | Usuario estándar para compras |
| `disenador` | disenador@nmcollections.com | `disenador123` | Diseñador | Acceso al canvas editor y creación de plantillas |

### 🎨 Canvas Editor y Personalización

El usuario **Diseñador** tiene acceso directo a:
- **Canvas Editor**: http://localhost:8004/personalizacion/canvas-editor/
- **Panel de administración**: Para gestionar plantillas y elementos
- **Creación de marcos**: Subida y gestión de marcos personalizados

**Credenciales de diseñador**: `disenador` / `disenador123`

> ⚠️ **IMPORTANTE**: El sistema NO incluye plantillas predeterminadas. Las plantillas deben ser creadas desde cero por el usuario Diseñador a través del Panel de Diseñador:
> - Acceder con usuario `disenador` / `disenador123`
> - Ir a http://localhost:8004/personalizacion/panel-diseñador/
> - Crear plantillas base antes de usar el Canvas Editor
> - Las plantillas son necesarias para la funcionalidad de personalización

## 🔄 Actualizaciones automáticas

La imagen Docker se construye desde GitHub:

1. **Para obtener cambios**: `docker pull mpowo/nmcollections:latest`
2. **Para rebuild manual**: 
   ```bash
   docker build --no-cache -t mpowo/nmcollections:latest .
   docker push mpowo/nmcollections:latest
   ```

## 🤝 Contribución

### Branches disponibles
- `main`: Producción estable y despliegue
- `deploy`: Prueba estables antes de produccion
- `DEVMatias`: Desarrollo colaborativo
- `DEVGustavo`: Desarrollo colaborativo
- `DEVJere`: Desarrollo colaborativo

## 📞 Soporte
- **Issues**: [GitHub Issues](https://github.com/Gustavo-Paredes/NMCollections.git)
- **Issues**: [GitHub Issues](https://github.com/MatiasParada/Portafolio/issues)
- **Documentación**: Este README
- **Docker Hub**: [mpowo/nmcollections](https://hub.docker.com/r/mpowo/nmcollections)

---

**Desarrollado con ❤️ para la comunidad de Trading Cards**
