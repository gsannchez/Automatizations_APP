# Local Development Setup

Follow these steps to set up and run the Auto Video Maker platform on your local machine.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Docker Desktop** (for PostgreSQL and Redis)
- **FFmpeg** installed and added to your system PATH

## Step 1: Start Infrastructure

Use Docker Compose to start the database and the message broker.

```bash
cd APP/
docker-compose up -d
```

Verify that `autovideo_postgres` and `autovideo_redis` are running.

## Step 2: Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd APP/backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate # Linux/Mac
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run migrations:
    ```bash
    alembic upgrade head
    ```
5.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```

## Step 3: Start Celery Worker

The worker processes the video generation pipeline.

1.  Open a new terminal in the backend directory and activate the venv.
2.  Run the worker:
    ```bash
    celery -A app.core.celery_app worker --pool=solo -l info
    ```
    _Note: `--pool=solo` is required for Windows compatibility._

## Step 4: Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd APP/frontend/auto-video-frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the Angular development server:
    ```bash
    npm start
    ```
4.  (Optional) Start Electron:
    ```bash
    npm run electron
    ```

## Step 5: Verify

- Backend API: `http://localhost:8000/docs`
- Frontend UI: `http://localhost:4200`
