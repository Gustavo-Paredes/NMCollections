# NM Collections - Plataforma Web & Personalización de Trading Cards

NM Collections es una plataforma completa para la compra, gestión y personalización de cartas coleccionables. Incluye un ecosistema de: catálogo e‑commerce, editor de cartas (Canvas), gestión de pedidos/pagos, API para aplicaciones móviles y flujo de usuarios con roles especializados.

---
## 📑 Índice
1. Visión General
2. Características Clave
3. Stack Tecnológico
4. Estructura del Proyecto
5. Instalación (Docker / Local)
6. Variables de Entorno
7. Flujo de Personalización (Canvas)
8. Flujo de Carrito y Pagos
9. Arquitectura Lógica de Apps
10. Usuarios y Roles
11. API (Resumen Inicial)
12. Comandos Útiles de Gestión
13. Estándares y Buenas Prácticas
14. Roadmap / Futuras Mejoras
15. Contribución
16. Soporte

---
## 1. Visión General
El objetivo es permitir al usuario final comprar cartas estándar y crear cartas personalizadas a partir de plantillas diseñadas por el rol Diseñador. El sistema integra pagos (Transbank), autenticación segura, y un backend modular mantenible con Django.

---
## 2. Características Clave
- 🛒 Carrito persistente por usuario
- 🎨 Editor Canvas (Fabric.js) para textos, imágenes y parámetros definidos en plantillas
- 🧱 Sistema de plantillas dinámicas (marco + elementos parametrizables)
- 💳 Pago seguro con Webpay Plus (entorno TEST)
- 📦 Gestión de pedidos y estados
- 🔐 Autenticación (Allauth + JWT para móvil) y usuarios custom (`AUTH_USER_MODEL`)
- 📱 API móvil (vía `apps.api_movil`) para sincronizar catálogo/pedidos
- 📨 Sistema de correo SMTP configurable
- 🗃 Archivos multimedia servidos desde `media/`
- 🧪 Configuración preparada para escalado a PostgreSQL en producción

---
## 3. Stack Tecnológico
| Capa | Tecnología | Uso |
|------|------------|-----|
| Backend | Django 5.2.6 | Core, ORM, Auth, Templates |
| API | Django REST Framework / SimpleJWT | Endpoints y JWT móvil |
| Tiempo real (futuro) | (pendiente) | Event-driven (sin WebSockets) |
| Frontend | HTML + Bootstrap 5 + JS | Interfaz web |
| Editor | Fabric.js | Render y manipulación de elementos en Canvas |
| BD | PostgreSQL (prod) / SQLite (dev rápido) | Persistencia |
| Pagos | Transbank SDK | Flujo Webpay Plus TEST |
| Static | WhiteNoise | Servir assets comprimidos |
| Contenedores | Docker | Empaquetado y despliegue |

Dependencias destacadas: `django-environ`, `django-cors-headers`, `drf-yasg` (Swagger), `django-extensions`, `reportlab` (PDF si se requiere), `rembg` (procesamiento imagen), `transbank-sdk`.

---
## 4. Estructura del Proyecto
```
NMCollections-web/
├── apps/
│   ├── api_movil/          # Serializers / endpoints para app móvil
│   ├── carrito/            # Modelos y vistas de Carrito
│   ├── core/               # Páginas base, catálogo general
│   ├── pagos/              # Flujo y callbacks de Webpay
│   ├── pedidos/            # Órdenes, checkout y estados
│   ├── personalizacion/    # Plantillas, cartas generadas, canvas
│   ├── productos/          # Catálogo, categorías, stock
│   ├── soporte/            # Chat / mensajería interna
│   └── usuarios/           # Modelo custom user y auth web
├── nmcollections/          # settings / urls / wsgi
├── templates/              # HTML organizado por módulo
├── static/                 # Assets fuente (css/js/img)
├── staticfiles/            # Resultado collectstatic
├── media/                  # Uploads (imagenes de cartas, marcos)
├── Dockerfile              # Build de imagen
├── create_users.py         # Script creación usuarios demo
└── requirements*.txt       # Dependencias
```

---
## 5. Instalación
### Opción A: Docker (Recomendado)
```bash
docker pull mpowo/nmcollections:latest
docker run -d --name nmcollections -p 8004:8004 mpowo/nmcollections:latest
# http://localhost:8004
```
Logs y verificación:
```bash
docker ps
docker logs nmcollections --tail 50
```

### Opción B: Local
```bash
git clone https://github.com/MatiasParada/Portafolio.git
cd Portafolio/NMCollections-web
python -m venv venv
./venv/Scripts/activate  # Windows
# source venv/bin/activate  # Linux / Mac
pip install -r requirements.txt
```
Migraciones y datos iniciales:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python create_users.py
python manage.py runserver 0.0.0.0:8000
```
# (Se removió soporte WebSocket/Daphne; usar runserver para desarrollo)

---
## 6. Variables de Entorno (.env ejemplo)
```env
DEBUG=True
SECRET_KEY=changeme_super_seguro
ALLOWED_HOSTS=localhost,127.0.0.1

dbname=nmcollections_db
user=postgres
password=postgres
host=localhost
port=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=app_password

WEBPAY_COMMERCE_CODE=597055555532
WEBPAY_API_KEY=579B...A36B1C
WEBPAY_ENVIRONMENT=TEST
SITE_URL=http://localhost:8000
```

---
## 7. Flujo de Personalización (Canvas)
1. Diseñador crea Plantilla: define marco (imagen base) + elementos (nombre, ataque, descripción, etc.).
2. Usuario final selecciona plantilla en el Canvas Editor.
3. Usuario edita campos (texto / imagen) → Fabric.js renderiza en tiempo real.
4. Se genera imagen final (almacenada en `media/`).
5. Carta personalizada se agrega al carrito como producto tipo `personalizado` con JSON interno (`personalizacion`).

Estructura simplificada del JSON guardado en `CarritoProducto.personalizacion`:
```json
{
   "carta_id": 42,
   "nombre_carta": "Dragon Verde Épico",
   "imagen": "/media/cartas/render_42.png",
   "parametros": [
      { "nombre": "ataque", "valor": 120 },
      { "nombre": "defensa", "valor": 95 }
   ]
}
```

---
## 8. Flujo de Carrito y Pagos
1. Usuario agrega productos estándar o cartas personalizadas.
2. `ver_carrito` calcula: `subtotal`, `costo_envio` (configurable), `total`.
3. Checkout abre modal → inicia flujo Webpay.
4. Transbank retorna token y redirige a página de confirmación.
5. Pedido se marca como pagado y se registra transacción.

Consideraciones futuras:
- Tarifas dinámicas de envío por comuna / región.
- Cupones y descuentos.
- Estados avanzados: `preparando`, `despachado`, `entregado`.

---
## 9. Arquitectura Lógica de Apps
- `usuarios`: Modelo custom extiende AbstractUser (probable campo `correo`).
- `productos`: CRUD de productos, categorías, precios base.
- `personalizacion`: Plantillas + cartas generadas + parámetros de carta.
- `carrito`: Relación usuario ↔ items (subtotal por línea = `cantidad * precio_unitario`).
- `pedidos`: Consolidación del carrito al confirmar (snapshot de precios).
- `pagos`: Integración con Transbank (crear, confirmar, fallbacks).
- `api_movil`: Serializers para exponer catálogo y pedidos (JWT).
- `soporte`: Mensajería simple (sin tiempo real todavía).

---
## 10. Usuarios y Roles (Demo)
| Rol | Email | Password | Permisos |
|-----|-------|----------|----------|
| Admin | admin@nmcollections.com | admin123 | Panel admin completo |
| Cliente | cliente@nmcollections.com | cliente123 | Comprar / ver pedidos |
| Diseñador | disenador@nmcollections.com | disenador123 | Crear plantillas / usar canvas |

> Ejecutado por `create_users.py` en instalación inicial.

---
## 11. API (Resumen Inicial)
Documentable vía `drf-yasg` (Swagger) en una futura ruta `/api/docs/`.

Endpoints típicos (conceptual):
- `POST /api/auth/login/` → JWT / sesión
- `GET /api/productos/` → listado filtrable
- `GET /api/pedidos/` → pedidos del usuario autenticado
- `POST /api/carrito/agregar/` → añadir producto
- `POST /api/personalizacion/render/` → generar carta

> Para uso móvil se recomienda token JWT (SimpleJWT configurado en `REST_FRAMEWORK`).

---
## 12. Comandos Útiles
```bash
python manage.py createsuperuser          # Crear superusuario
python manage.py dumpdata productos > productos.json   # Exportar datos
python manage.py loaddata productos.json  # Importar datos
python manage.py shell_plus               # Consola avanzada (django-extensions)
python manage.py show_urls                # Listar rutas (django-extensions)
```

---
## 13. Estándares y Buenas Prácticas
- Separar lógica en servicios en caso de crecer (`services/` futuros).
- Evitar lógica pesada en vistas → mover a métodos de modelo o utils.
- Usar `select_related` y `prefetch_related` en consultas con relaciones.
- No almacenar blobs de imagen en DB: usar `ImageField` + rutas (`media/`).
- Preparar para CDN/Cloud Storage (S3, Cloudinary) en entorno productivo.
- Revisar seguridad: rotar `SECRET_KEY`, configurar `SECURE_*` en producción.

---
## 14. Roadmap / Futuras Mejoras
- Integración almacenamiento externo (S3 / Cloudinary).
- Sistema de cupones y descuentos.
- Seguimiento avanzado de envíos (integración con couriers).
- Internacionalización completa (i18n más textos).
- Mejorar editor (capas, filtros, recortes avanzados).
- Integración tiempo real (futura, sin WebSockets actualmente).
- Panel analytics (ventas, uso de plantillas, conversión).

---
## 15. Contribución
Branches:
- `main` (estable)
- `deploy` (pre-producción)
- `DEVMatias`, `DEVGustavo`, `DEVJere` (features / trabajo colaborativo)

Workflow sugerido:
1. Crear branch desde `deploy`.
2. Commits pequeños y descriptivos (ES / EN consistente).
3. Pull Request con resumen + pruebas manuales.
4. Code review y merge a `deploy` → luego promoción a `main`.

Convenciones:
- Python: PEP8, evitar lógica circular.
- Templates: reutilizar bloques `extends` y componentes.
- JS: funciones puras cuando sea posible; Fabric.js encapsular helpers.

---
## 16. Soporte
| Recurso | Enlace |
|---------|--------|
| Issues (Portafolio) | https://github.com/MatiasParada/Portafolio/issues |
| Docker Hub | https://hub.docker.com/r/mpowo/nmcollections |
| Documentación API (futuro) | /api/docs/ |

---
**Desarrollado con ❤️ para la comunidad de Trading Cards**
