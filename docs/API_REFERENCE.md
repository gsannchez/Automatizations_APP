# Referencia de la API

Todas las peticiones a la API deben realizarse a la URL base: `http://localhost:8000/api/v1`.

## Endpoints de Autenticación

### POST `/auth/register`

- **Propósito**: Crear una nueva cuenta de usuario.
- **Entrada**: `email`, `password`.
- **Salida**: `access_token`, `refresh_token`.
- **Autenticación**: Ninguna.

### POST `/auth/login`

- **Propósito**: Autenticar a un usuario existente.
- **Entrada**: `email`, `password`.
- **Salida**: `access_token`, `refresh_token`.
- **Autenticación**: Ninguna (Límite de peticiones: 5 peticiones/min).

### POST `/auth/refresh`

- **Propósito**: Obtener un nuevo token de acceso usando un token de actualización.
- **Entrada**: `refresh_token`.
- **Salida**: `access_token`.
- **Autenticación**: Ninguna (requiere un token de actualización válido en el cuerpo de la petición).

### GET `/auth/me`

- **Propósito**: Obtener el perfil del usuario que ha iniciado sesión actualmente.
- **Entrada**: Ninguna.
- **Salida**: `id`, `email`, `plan`, `created_at`.
- **Autenticación**: Requerida (Bearer JWT).

---

## Endpoints de Video

### GET `/videos`

- **Propósito**: Listar todos los videos que pertenecen al usuario autenticado.
- **Entrada**: `page` (por defecto 1), `limit` (por defecto 20).
- **Salida**: Lista paginada de videos (`items`, `total`, `page`, `limit`).
- **Autenticación**: Requerida (Bearer JWT).

### POST `/videos`

- **Propósito**: Inicializar un nuevo registro de video.
- **Entrada**: `template_id`, `title`, `platform`, `topic`.
- **Salida**: Objeto del video creado.
- **Autenticación**: Requerida (Bearer JWT).

### GET `/videos/{id}`

- **Propósito**: Obtener los detalles de un video específico.
- **Entrada**: `id` (UUID).
- **Salida**: Objeto del video.
- **Autenticación**: Requerida (Bearer JWT). Retorna 404 si no es el propietario.

### GET `/videos/{id}/status`

- **Propósito**: Endpoint ligero para consultar el estado actual de generación.
- **Entrada**: `id` (UUID).
- **Salida**: `status`, `error_message`, `error_step`.
- **Autenticación**: Requerida (Bearer JWT).

### GET `/videos/{id}/download`

- **Propósito**: Obtener una URL segura de descarga para un video completado.
- **Entrada**: `id` (UUID).
- **Salida**: `download_url`.
- **Autenticación**: Requerida (Bearer JWT). Retorna 409 si el estado no es `DONE`.

### DELETE `/videos/{id}`

- **Propósito**: Eliminar lógicamente (soft-delete) un video.
- **Entrada**: `id` (UUID).
- **Salida**: `{"deleted": true}`.
- **Autenticación**: Requerida (Bearer JWT).

### POST `/videos/{id}/generate`

- **Propósito**: Iniciar la tubería asincrónica de generación para un video.
- **Entrada**: `id` (UUID), opcional `music_file`.
- **Salida**: Mensaje de confirmación.
- **Autenticación**: Requerida (Bearer JWT).
