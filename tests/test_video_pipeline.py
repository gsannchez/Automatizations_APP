import pytest
from httpx import AsyncClient
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.main import app

@pytest.fixture
async def auth_headers():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        email = f"pipe_{os.urandom(4).hex()}@example.com"
        await ac.post("/api/v1/auth/register", json={"email": email, "password": "password"})
        login = await ac.post("/api/v1/auth/login", json={"email": email, "password": "password"})
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

@pytest.mark.asyncio
async def test_pipeline_status_transitions(auth_headers):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # 1. Create video
        create_resp = await ac.post("/api/v1/videos/", json={
            "title": "Pipeline Test",
            "template_id": "00000000-0000-0000-0000-000000000000",
            "platform": "TIKTOK"
        }, headers=auth_headers)
        video_id = create_resp.json()["id"]
        
        # 2. Initial Status
        status_resp = await ac.get(f"/api/v1/videos/{video_id}/status", headers=auth_headers)
        assert status_resp.json()["status"] == "QUEUED"
        
        # 3. Simulate Worker Updates (via PATCH if allowed, or we just trust the orchestrator)
        # Note: In a real E2E, we'd trigger /generate and poll.
        # For this component test, we verify the status endpoint returns what's in DB.
        
        await ac.patch(f"/api/v1/videos/{video_id}", json={"status": "PROCESSING"}, headers=auth_headers)
        status_resp = await ac.get(f"/api/v1/videos/{video_id}/status", headers=auth_headers)
        assert status_resp.json()["status"] == "PROCESSING"

        await ac.patch(f"/api/v1/videos/{video_id}", json={"status": "DONE", "storage_key": "user/vid/final.mp4"}, headers=auth_headers)
        status_resp = await ac.get(f"/api/v1/videos/{video_id}/status", headers=auth_headers)
        assert status_resp.json()["status"] == "DONE"
