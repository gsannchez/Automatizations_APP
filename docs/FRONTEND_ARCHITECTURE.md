# Arquitectura del Frontend

## Descripción General

El frontend es una aplicación de **Angular** diseñada para una alta capacidad de respuesta y retroalimentación en tiempo real. Utiliza una arquitectura basada en componentes y la inyección de dependencias integrada de Angular para la modularidad.

## Estructura de Directorios

```text
src/app/
├── features/        # Módulos funcionales (Panel de control, Inicio de sesión, Registro)
├── services/        # Lógica de negocio centralizada y llamadas a la API
├── guards/          # Lógica de protección de rutas
├── interceptors/    # Modificación de peticiones/respuestas HTTP
├── layout/          # Componentes de interfaz de usuario comunes (Barra de navegación, Barra lateral)
└── app.routes.ts    # Configuración de navegación principal
```

## Componentes Principales

### Servicios

#### AuthService (Servicio de Autenticación)

- Gestiona el registro y la autenticación de usuarios.
- Gestiona los tokens JWT en `localStorage`.
- Proporciona un `observable` del estado del usuario actual.
- Maneja la lógica de actualización (refresh) del token automáticamente.

#### VideoService (Servicio de Video)

- Gestiona todas las interacciones relacionadas con videos con el backend.
- Proporciona métodos para listar videos, crear nuevos y eliminarlos.
- Maneja la transformación del flujo (stream) de descarga.

### Guards (Guardias de Ruta)

#### AuthGuard (Guardia de Autenticación)

- Protege las rutas privadas (ej., `/dashboard`).
- Redirige a los usuarios no autenticados a la página de `/login`.

### Interceptores

#### AuthInterceptor (Interceptor de Autenticación)

- Adjunta automáticamente la cabecera JWT `Authorization: Bearer <token>` a todas las peticiones salientes.
- Intercepta las respuestas `401 Unauthorized` para activar la actualización (refresh) del token o el cierre de la sesión.

## Sistema de Sondeo (Polling)

Dado que la generación de video es un proceso asíncrono que puede tardar varios minutos, el frontend implementa un sistema de sondeo inteligente:

1. **Activador (Trigger)**: Cuando un video se encuentra en un estado no terminal (ej., `QUEUED`, `PROCESSING`), se inicia un mecanismo de sondeo.
2. **Mecanismo**: Utiliza `timer` o `interval` de RxJS dentro del componente Listado de Videos.
3. **Frecuencia**: Típicamente realiza sondeos cada 5-10 segundos.
4. **Terminación**: Detiene el sondeo cuando el video alcanza un estado terminal (`DONE` o `FAILED`).
5. **Eficiencia**: Solo realiza sondeos para los videos que están actualmente visibles y activos.

## Progreso Dinámico

El progreso se muestra al usuario en función del estado actual del video y del paso detallado reportado por el sistema de seguimiento de `VideoJob`. Esto proporciona una sensación de "en vivo" (live) al proceso de generación.
