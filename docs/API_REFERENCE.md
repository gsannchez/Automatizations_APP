# API Reference

All API requests must be made to the base URL: `http://localhost:8000/api/v1`.

## Authentication Endpoints

### POST `/auth/register`

- **Purpose**: Create a new user account.
- **Input**: `email`, `password`.
- **Output**: `access_token`, `refresh_token`.
- **Authentication**: None.

### POST `/auth/login`

- **Purpose**: Authenticate an existing user.
- **Input**: `email`, `password`.
- **Output**: `access_token`, `refresh_token`.
- **Authentication**: None (Rate-limited: 5 requests/min).

### POST `/auth/refresh`

- **Purpose**: Obtain a new access token using a refresh token.
- **Input**: `refresh_token`.
- **Output**: `access_token`.
- **Authentication**: None (requires a valid refresh token in body).

### GET `/auth/me`

- **Purpose**: Retrieve the profile of the currently logged-in user.
- **Input**: None.
- **Output**: `id`, `email`, `plan`, `created_at`.
- **Authentication**: Required (Bearer JWT).

---

## Video Endpoints

### GET `/videos`

- **Purpose**: List all videos owned by the authenticated user.
- **Input**: `page` (default 1), `limit` (default 20).
- **Output**: Paginated list of videos (`items`, `total`, `page`, `limit`).
- **Authentication**: Required (Bearer JWT).

### POST `/videos`

- **Purpose**: Initialize a new video record.
- **Input**: `template_id`, `title`, `platform`, `topic`.
- **Output**: Created video object.
- **Authentication**: Required (Bearer JWT).

### GET `/videos/{id}`

- **Purpose**: Retrieve details of a specific video.
- **Input**: `id` (UUID).
- **Output**: Video object.
- **Authentication**: Required (Bearer JWT). Returns 404 if not owned.

### GET `/videos/{id}/status`

- **Purpose**: Lightweight endpoint for polling the current generation status.
- **Input**: `id` (UUID).
- **Output**: `status`, `error_message`, `error_step`.
- **Authentication**: Required (Bearer JWT).

### GET `/videos/{id}/download`

- **Purpose**: Get a secure download URL for a completed video.
- **Input**: `id` (UUID).
- **Output**: `download_url`.
- **Authentication**: Required (Bearer JWT). Returns 409 if status is not `DONE`.

### DELETE `/videos/{id}`

- **Purpose**: Soft-delete a video.
- **Input**: `id` (UUID).
- **Output**: `{"deleted": true}`.
- **Authentication**: Required (Bearer JWT).

### POST `/videos/{id}/generate`

- **Purpose**: Start the asynchronous generation pipeline for a video.
- **Input**: `id` (UUID), optional `music_file`.
- **Output**: Confirmation message.
- **Authentication**: Required (Bearer JWT).
