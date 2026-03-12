# Frontend Architecture

## Overview

The frontend is an **Angular** application designed for high responsiveness and real-time feedback. It uses a component-based architecture and Angular's built-in dependency injection for modularity.

## Directory Structure

```text
src/app/
├── features/        # Functional modules (Dashboard, Login, Register)
├── services/        # Centralized business logic and API calls
├── guards/          # Route protection logic
├── interceptors/    # HTTP request/response modification
├── layout/          # Common UI components (Navbar, Sidebar)
└── app.routes.ts    # Main navigation configuration
```

## Core Components

### Services

#### AuthService

- Handles user registration and authentication.
- Manages JWT tokens in `localStorage`.
- Provides an `observable` of the current user's state.
- Handles token refresh logic automatically.

#### VideoService

- Manages all video-related interactions with the backend.
- Provides methods for listing videos, creating new ones, and deleting them.
- Handles the download stream transformation.

### Guards

#### AuthGuard

- Protects private routes (e.g., `/dashboard`).
- Redirects unauthenticated users to the `/login` page.

### Interceptors

#### AuthInterceptor

- Automatically attaches the JWT `Authorization: Bearer <token>` header to all outgoing requests.
- Intercepts `401 Unauthorized` responses to trigger token refreshing or session logout.

## Polling System

Since video generation is an asynchronous process that can take several minutes, the frontend implements an intelligent polling system:

1. **Trigger**: When a video is in a non-terminal status (e.g., `QUEUED`, `PROCESSING`), a polling mechanism is started.
2. **Mechanism**: Uses RxJS `timer` or `interval` within the Video List component.
3. **Frequency**: Typically polls every 5-10 seconds.
4. **Termination**: Stops polling when the video reaches a terminal status (`DONE` or `FAILED`).
5. **Efficiency**: Only polls for videos that are currently visible and active.

## Dynamic Progress

Progress is displayed to the user based on the video's current status and the detailed step reported by the `VideoJob` tracking system. This provides a "live" feel to the generation process.
