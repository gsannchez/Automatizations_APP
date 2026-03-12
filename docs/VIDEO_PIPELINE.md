# Video Pipeline

## Overview

The video generation process is orchestrated as a series of discrete, idempotent steps executed by Celery workers. This ensures reliability and allows the system to recover from failures without restarting the entire process.

## Pipeline Steps

The pipeline follows a frozen order:

1.  **QUEUED**: Initial state when the job is added to the Redis queue.
2.  **SCRIPTING**: Generates the text script and scenes using AI.
3.  **SCRIPT_VALIDATED**: Ensures the generated script meets quality and safety standards.
4.  **IMAGE_GENERATION**: Creates visual assets for each scene using AI image generators.
5.  **VOICE_SYNTHESIS**: Generates audio narration for each scene using Text-to-Speech (TTS).
6.  **MEDIA_COMPOSITION**: Combines visual and audio assets into a raw video stream.
7.  **ENCODING**: Finalizes the video file using FFmpeg (bitrate optimization, metadata).
8.  **UPLOADING**: Moves the final file to the designated storage (Local or Cloud).
9.  **DONE**: The video is ready for download and the status is finalized.

## Reliable Orchestration

### VideoJob Tracking

Each step execution is logged in the `VideoJob` table. This record includes:

- Step name.
- Start and end timestamps.
- Success/Failure status.
- Error messages (if applicable).

### Idempotency

Before starting a step, the orchestrator checks if that specific step has already been marked as `success` in the `VideoJob` table for the current `video_id`. If it has, the step is skipped. This allows the workflow to be re-run safely multiple times.

### Crash Recovery

If a worker crashes mid-task:

1.  The `VideoJob` entry for the active step remains without an `ended_at` timestamp.
2.  The `GeneratedVideo` status remains in the last attempted step.
3.  Upon restart or retry, the orchestrator uses `get_resume_index()` to find the first uncompleted step and resumes from there.

### Retry Logic

- Failed steps are captured and the `retry_count` of the video is incremented.
- The system automatically retires the workflow using an exponential backoff (e.g., 60 seconds).
- A video is marked as `FAILED` only after reaching the maximum number of retries (currently 3).
