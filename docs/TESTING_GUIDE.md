# Testing Guide

This document outlines the procedures for verifying the stability and correctness of the platform.

## Automated Testing

Automated tests are located in the `tests/` directory and use the `pytest` framework.

### Running Tests

To run all automated tests, follow these steps:

1.  Navigate to the project root.
2.  Activate the backend virtual environment.
3.  Execute the test runner:

```bash
cd APP/backend
pytest ../tests/
```

### Test Suite Overview

- `test_auth_system.py`: Verifies user registration, login, token refresh, and protected route access.
- `test_video_crud.py`: Ensures videos can be created, listed, retrieved, and deleted.
- `test_video_pipeline.py`: Tests the full pipeline status transitions from QUEUED to DONE.
- `test_download_endpoint.py`: Confirms that download links are only available for completed videos.
- `test_video_ownership.py`: Validates that users cannot access each other's videos.
- `test_pagination.py`: Tests the limit and offset logic of the video list.
- `e2e_test_flow.py`: A script that simulates a complete user journey through the platform.

---

## Manual Verification Procedures

Follow these steps to manually verify the core functionality of the platform.

### 1. User Onboarding

1.  Open the application in a browser.
2.  Click on **Register** and create a new account.
3.  Verify that you are automatically redirected to the **Login** page or **Dashboard**.
4.  Logout and log back in to ensure session persistence.

### 2. Video Creation & Progress

1.  From the Dashboard, click **Create New Video**.
2.  Fill in the template details and click **Generate**.
3.  Observe the video list:
    - The new video should appear with status `QUEUED`.
    - Within seconds, the status should transition to `PROCESSING` (showing specific pipeline steps).
    - Verify that the progress bar or status indicators update in real-time.

### 3. File Verification

1.  Wait until the video status is `DONE`.
2.  Click the **Download** button.
3.  Verify that the video file downloads correctly and can be played.
4.  Navigate to the `APP/backend/videos/` directory and ensure the file exists in the correct user subfolder.

### 4. Security & Separation

1.  Open an Incognito/Private window.
2.  Login with a **different** account.
3.  Verify that the video list is empty or does not show videos from the first account.
4.  Attempt to manually access a video ID from the first account via the URL (if applicable) and verify it returns a 404 or access denied.

### 5. Pagination

1.  Create more than 20 videos (or the current page limit).
2.  Verify that pagination controls appear at the bottom of the list.
3.  Click through the pages and ensure different videos are displayed.
