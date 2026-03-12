import pytest
from httpx import AsyncClient
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.main import app

@pytest.fixture
async def auth_headers():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        email = f"page_{os.urandom(4).hex()}@example.com"
        await ac.post("/api/v1/auth/register", json={"email": email, "password": "password"})
        login = await ac.post("/api/v1/auth/login", json={"email": email, "password": "password"})
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

@pytest.mark.asyncio
async def test_pagination_logic(auth_headers):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # 1. Create 5 videos
        for i in range(5):
            await ac.post("/api/v1/videos/", json={
                "title": f"Video {i}",
                "template_id": "00000000-0000-0000-0000-000000000000",
                "platform": "TIKTOK"
            }, headers=auth_headers)
        
        # 2. Test limit=2
        resp = await ac.get("/api/v1/videos/?page=1&limit=2", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["limit"] == 2
        
        # 3. Test second page
        resp_p2 = await ac.get("/api/v1/videos/?page=2&limit=2", headers=auth_headers)
        data_p2 = resp_p2.json()
        assert len(data_p2["items"]) == 2
        assert data_p2["page"] == 2
        
        # Verify items are different
        assert data["items"][0]["id"] != data_p2["items"][0]["id"]
