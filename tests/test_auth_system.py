import pytest
from httpx import AsyncClient
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.main import app

BASE_URL = "http://testserver/api/v1/auth"

@pytest.mark.asyncio
async def test_auth_workflow():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # 1. Register
        email = f"test_{os.urandom(4).hex()}@example.com"
        password = "testpassword123"
        
        reg_resp = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": password
        })
        assert reg_resp.status_code == 201
        tokens = reg_resp.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # 2. Login
        login_resp = await ac.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # 3. Access Protected Endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        me_resp = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == email
        
        # 4. Refresh Token
        refresh_resp = await ac.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_resp.status_code == 200
        new_access_token = refresh_resp.json()["access_token"]
        assert new_access_token != access_token
        
        # 5. Access with new token
        headers = {"Authorization": f"Bearer {new_access_token}"}
        me_resp_new = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_resp_new.status_code == 200
        assert me_resp_new.json()["email"] == email
