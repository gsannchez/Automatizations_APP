import pytest
from httpx import AsyncClient
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.main import app

@pytest.fixture
async def auth_headers():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        email = f"dl_{os.urandom(4).hex()}@example.com"
        await ac.post("/api/v1/auth/register", json={"email": email, "password": "password"})
        login = await ac.post("/api/v1/auth/login", json={"email": email, "password": "password"})
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

@pytest.mark.asyncio
async def test_download_availability(auth_headers):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # 1. Create video
        create_resp = await ac.post("/api/v1/videos/", json={
            "title": "Download Test",
            "template_id": "00000000-0000-0000-0000-000000000000",
            "platform": "TIKTOK"
        }, headers=auth_headers)
        video_id = create_resp.json()["id"]
        
        # 2. Try download while QUEUED -> Expect 409
        dl_resp = await ac.get(f"/api/v1/videos/{video_id}/download", headers=auth_headers)
        assert dl_resp.status_code == 409
        
        # 3. Mark as DONE
        await ac.patch(f"/api/v1/videos/{video_id}", json={"status": "DONE"}, headers=auth_headers)
        
        # 4. Try download while DONE -> Expect 200 and URL
        dl_resp_done = await ac.get(f"/api/v1/videos/{video_id}/download", headers=auth_headers)
        assert dl_resp_done.status_code == 200
        assert "download_url" in dl_resp_done.json()
