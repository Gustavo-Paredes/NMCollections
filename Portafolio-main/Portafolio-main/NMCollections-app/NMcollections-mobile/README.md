# NMCollections Mobile

NMCollections Mobile es la aplicación móvil de la plataforma NMCollections, desarrollada con React Native y Expo. Permite a los usuarios navegar el catálogo de productos personalizados, gestionar su carrito, realizar pedidos, jugar minijuegos, ver notificaciones y contactar soporte.

## Funcionalidades principales
- **Catálogo**: Visualiza productos disponibles y personalizados.
- **Carrito**: Añade productos y gestiona compras.
- **Pedidos**: Consulta el historial y estado de tus pedidos.
- **Perfil**: Edita tu información personal y dirección.
- **Juegos**: Accede a minijuegos y logros.
- **Soporte**: Contacta al equipo de soporte.
- **Notificaciones**: Recibe avisos importantes.

## Requisitos previos
- Node.js >= 18
- npm >= 9
- Expo CLI (`npm install -g expo-cli`)

## Instalación
1. Clona el repositorio y entra a la carpeta:
   ```sh
   git clone https://github.com/MatiasParada/Portafolio.git
   cd NMCollections-app/NMcollections-mobile
   ```
2. Instala las dependencias:
   ```sh
   npm install
   ```

## Levantar la app en modo desarrollo
Puedes iniciar la app en modo desarrollo usando Expo:

```sh
npx expo start
```

Esto abrirá el panel de Expo. Desde ahí puedes:
- Escanear el QR con la app Expo Go en tu teléfono
- Ejecutar en un emulador Android/iOS
- Abrir en navegador web

### Comandos útiles
- `npm start` — Inicia el servidor de desarrollo Expo
- `npm run android` — Ejecuta en emulador Android
- `npm run ios` — Ejecuta en emulador iOS (MacOS)
- `npm run web` — Ejecuta en navegador web

## Configuración de API
La app consume la API de NMCollections Web. Por defecto, la URL está configurada en los archivos de contexto y pantallas (ejemplo: `https://zkbc59xz-8000.brs.devtunnels.ms/api/v1/`). Modifica la IP/host según tu entorno.

## Estructura principal
- `App.js` / `App.tsx`: Punto de entrada y navegación principal
- `screens/`: Pantallas principales (Catálogo, Carrito, Pedidos, Perfil, Juegos, Soporte, Notificaciones)
- `contexts/`: Contextos globales para productos, usuario, carrito, etc.
- `assets/`: Imágenes, íconos y recursos

## Notas
- Para desarrollo local, asegúrate que el backend Django esté corriendo y accesible desde tu dispositivo/emulador.
- Si usas Expo Go, ambos dispositivos deben estar en la misma red.

## Contacto y soporte
Para dudas o soporte, contacta al equipo de NMCollections.
