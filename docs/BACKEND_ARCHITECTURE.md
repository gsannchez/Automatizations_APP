# Backend Architecture

## Overview

The backend is built with **FastAPI**, providing a high-performance, asynchronous REST API. It follows a modular structure separated into API routes, core logic, models, schemas, and services.

## Directory Structure

```text
backend/app/
├── api/             # API Routers (v1)
├── core/            # Core configurations (DB, security, Celery)
├── models/          # SQLModel database models
├── schemas/         # Pydantic models for request/response validation
├── services/        # Business logic and external integrations
├── utils/           # Helper utilities
└── main.py          # Application entry point
```

## Core Components

### FastAPI Routers

The API is versioned and split into functional routers:

- `auth.py`: Registration, login, and token management.
- `videos.py`: CRUD operations for generated videos and status tracking.
- `templates.py`: Management of video templates.
- `ai.py`: Manual triggers for AI-related tasks.

### Authentication System

Handles security using JWT (JSON Web Tokens):

- **Access Tokens**: Short-lived (e.g., 30m) for authorizing requests.
- **Refresh Tokens**: Long-lived for obtaining new access tokens without re-logging.
- **Password Hashing**: Uses Passlib with bcrypt.

### VideoJob Step Tracking

The system uses a granular tracking mechanism:

- Every video generation task is divided into discrete steps (e.g., `SCRIPTING`, `IMAGE_GENERATION`).
- Each step is recorded in the `VideoJob` table.
- This allows the system to resume from the last successful step if a worker crashes (**Idempotency**).

### Database Models

#### User

- Manages account details, subscription plans, and resource usage.
- Uses UUID v7 for time-ordered primary keys.

#### GeneratedVideo

- The main entity representing a video being created or already rendered.
- Linked to a `User` for ownership and a `Template` for structure.
- Tracks `status` (QUEUED, PROCESSING, DONE, FAILED).

#### VideoJob

- Tracks individual execution steps within the generation pipeline for a specific video.

#### Template

- Defines the structure and parameters for video generation (e.g., niche, style, duration).

#### Asset

- Represents modular media components (images, audio) generated during the process.

### Storage Abstraction

The system uses a `StorageService` to abstract file operations. While currently using **Local Storage**, the implementation is designed to be easily swapped for **Cloud Storage (S3)** in the next phase.

- Final videos are stored with a unique `storage_key`.
- Only relative paths are stored in the database.

### Download Endpoint

- Provides a secure way to access final video files.
- Ensures only the owner of the video can generate a download link.
- Returns a temporary URL or streams the file directly.
