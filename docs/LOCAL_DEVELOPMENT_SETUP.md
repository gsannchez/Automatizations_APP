# Configuración de Desarrollo Local

Sigue estos pasos para configurar y ejecutar la plataforma Auto Video Maker en tu máquina local.

## Requisitos Previos

- **Python 3.10+**
- **Node.js 18+** y **npm**
- **Docker Desktop** (para PostgreSQL y Redis)
- **FFmpeg** instalado y añadido al PATH de tu sistema

## Paso 1: Iniciar la Infraestructura

Utiliza Docker Compose para iniciar la base de datos y el intermediario de mensajes (message broker).

```bash
cd APP/
docker-compose up -d
```

Verifica que `autovideo_postgres` y `autovideo_redis` estén en ejecución.

## Paso 2: Configuración del Backend

1.  Navega hasta el directorio del backend:
    ```bash
    cd APP/backend
    ```
2.  Crea y activa un entorno virtual:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate # Linux/Mac
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecuta las migraciones:
    ```bash
    alembic upgrade head
    ```
5.  Inicia el servidor FastAPI:
    ```bash
    uvicorn app.main:app --reload
    ```

## Paso 3: Iniciar el Celery Worker

El worker procesa la tubería de generación de video.

1.  Abre una nueva terminal en el directorio del backend y activa el entorno virtual (venv).
2.  Ejecuta el worker:
    ```bash
    celery -A app.core.celery_app worker --pool=solo -l info
    ```
    _Nota: `--pool=solo` es necesario para compatibilidad con Windows._

## Paso 4: Configuración del Frontend

1.  Navega hasta el directorio del frontend:
    ```bash
    cd APP/frontend/auto-video-frontend
    ```
2.  Instala las dependencias:
    ```bash
    npm install
    ```
3.  Inicia el servidor de desarrollo de Angular:
    ```bash
    npm start
    ```
4.  (Opcional) Inicia Electron:
    ```bash
    npm run electron
    ```

## Paso 5: Verificar

- API del Backend: `http://localhost:8000/docs`
- Interfaz del Frontend: `http://localhost:4200`
