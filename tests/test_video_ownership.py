import pytest
from httpx import AsyncClient
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.main import app

async def get_auth_headers(email):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        await ac.post("/api/v1/auth/register", json={"email": email, "password": "password"})
        login = await ac.post("/api/v1/auth/login", json={"email": email, "password": "password"})
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

@pytest.mark.asyncio
async def test_multiuser_isolation():
    # Setup User A and User B
    headers_a = await get_auth_headers(f"user_a_{os.urandom(4).hex()}@test.com")
    headers_b = await get_auth_headers(f"user_b_{os.urandom(4).hex()}@test.com")
    
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # 1. User A creates a video
        create_resp = await ac.post("/api/v1/videos/", json={
            "title": "A's Private Video",
            "template_id": "00000000-0000-0000-0000-000000000000",
            "platform": "TIKTOK"
        }, headers=headers_a)
        video_id = create_resp.json()["id"]
        
        # 2. User B tries to access User A's video
        get_resp = await ac.get(f"/api/v1/videos/{video_id}", headers=headers_b)
        assert get_resp.status_code == 404  # Should be hidden from other users
        
        # 3. User B tries to delete User A's video
        del_resp = await ac.delete(f"/api/v1/videos/{video_id}", headers=headers_b)
        assert del_resp.status_code == 404
        
        # 4. User B lists videos -> should not see User A's video
        list_resp = await ac.get("/api/v1/videos/", headers=headers_b)
        items = list_resp.json()["items"]
        assert all(v["id"] != video_id for v in items)
