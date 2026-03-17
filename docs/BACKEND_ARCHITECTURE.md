# Arquitectura del Backend

## Descripción General

El backend está construido con **FastAPI**, proporcionando una API REST asíncrona de alto rendimiento. Sigue una estructura modular separada en rutas de API, lógica principal, modelos, esquemas y servicios.

## Estructura de Directorios

```text
backend/app/
├── api/             # Enrutadores de API (v1)
├── core/            # Configuraciones principales (Base de datos, seguridad, Celery)
├── models/          # Modelos de base de datos SQLModel
├── schemas/         # Modelos Pydantic para validación de peticiones/respuestas
├── services/        # Lógica de negocio e integraciones externas
├── utils/           # Utilidades auxiliares
└── main.py          # Punto de entrada de la aplicación
```

## Componentes Principales

### Enrutadores FastAPI (Routers)

La API está versionada y dividida en enrutadores funcionales:

- `auth.py`: Registro, inicio de sesión y gestión de tokens.
- `videos.py`: Operaciones CRUD para videos generados y seguimiento de estado.
- `templates.py`: Gestión de plantillas de video.
- `ai.py`: Activadores manuales para tareas relacionadas con IA.

### Sistema de Autenticación

Maneja la seguridad utilizando JWT (JSON Web Tokens):

- **Tokens de Acceso (Access Tokens)**: De corta duración (ej. 30m) para autorizar peticiones.
- **Tokens de Actualización (Refresh Tokens)**: De larga duración para obtener nuevos tokens de acceso sin tener que volver a iniciar sesión.
- **Hash de Contraseñas**: Utiliza Passlib con bcrypt.

### Seguimiento de Pasos de VideoJob

El sistema utiliza un mecanismo de seguimiento granular:

- Cada tarea de generación de video se divide en pasos concretos (ej. `SCRIPTING`, `IMAGE_GENERATION`).
- Cada paso se registra en la tabla `VideoJob`.
- Esto permite al sistema reanudar desde el último paso exitoso si un trabajador (worker) falla (**Idempotencia**).

### Modelos de Base de Datos

#### User (Usuario)

- Gestiona los detalles de la cuenta, planes de suscripción y uso de recursos.
- Utiliza UUID v7 para claves primarias ordenadas por tiempo.

#### GeneratedVideo (Video Generado)

- La entidad principal que representa un video en proceso de creación o ya renderizado.
- Enlazado a un `User` por propiedad y a un `Template` por estructura.
- Rastrea el estado (`status`: QUEUED, PROCESSING, DONE, FAILED).

#### VideoJob (Trabajo de Video)

- Rastrea los pasos de ejecución individuales dentro de la tubería de generación para un video específico.

#### Template (Plantilla)

- Define la estructura y los parámetros para la generación de video (ej. nicho, estilo, duración).

#### Asset (Activo)

- Representa componentes multimedia modulares (imágenes, audio) generados durante el proceso.

### Abstracción de Almacenamiento

El sistema utiliza un `StorageService` para abstraer las operaciones de archivos. Aunque actualmente utiliza **Almacenamiento Local**, la implementación está diseñada para ser fácilmente intercambiable por **Almacenamiento en la Nube (S3)** en la siguiente fase.

- Los videos finales se almacenan con un `storage_key` único.
- Solo las rutas relativas se almacenan en la base de datos.

### Endpoint de Descarga

- Proporciona una forma segura de acceder a los archivos de video finales.
- Asegura que solo el propietario del video pueda generar un enlace de descarga.
- Devuelve una URL temporal o transmite (streams) el archivo directamente.
