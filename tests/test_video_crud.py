import pytest
from httpx import AsyncClient
import sys
import os
from uuid import UUID

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.main import app

@pytest.fixture
async def auth_headers():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        email = f"crud_{os.urandom(4).hex()}@example.com"
        await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "password"
        })
        login = await ac.post("/api/v1/auth/login", json={
            "email": email,
            "password": "password"
        })
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_video_crud_workflow(auth_headers):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # 1. Create
        create_data = {
            "title": "Test Video",
            "template_id": "00000000-0000-0000-0000-000000000000", # Placeholder UUID
            "platform": "TIKTOK",
            "topic": "Testing CRUD"
        }
        # Note: Need a real template ID if DB has constraints, but usually SQLModel allows it if not checked
        # Let's assume we can create one or use a dummy.
        
        create_resp = await ac.post("/api/v1/videos/", json=create_data, headers=auth_headers)
        assert create_resp.status_code == 200
        video = create_resp.json()
        video_id = video["id"]
        assert video["title"] == "Test Video"
        
        # 2. List
        list_resp = await ac.get("/api/v1/videos/", headers=auth_headers)
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] >= 1
        assert any(v["id"] == video_id for v in data["items"])
        
        # 3. Get
        get_resp = await ac.get(f"/api/v1/videos/{video_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == "Test Video"
        
        # 4. Delete
        del_resp = await ac.delete(f"/api/v1/videos/{video_id}", headers=auth_headers)
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True
        
        # 5. Verify 404 after delete
        get_gone = await ac.get(f"/api/v1/videos/{video_id}", headers=auth_headers)
        assert get_gone.status_code == 404
