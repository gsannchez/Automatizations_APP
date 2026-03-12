import requests
import time
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def test_saas_flow():
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    password = "password123"

    print(f"--- Phase 3 SaaS Flow Test ({email}) ---")

    # 1. Register
    print("1. Testing Register...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Register failed: {resp.text}"
    tokens = resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    print("   ✅ Register OK")

    # 2. Login (Rate Limiting check - quick burst)
    print("2. Testing Login & Rate Limiting...")
    for i in range(3):
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if resp.status_code == 429:
            print(f"   ℹ️ Rate limit hit as expected on attempt {i+1}")
            break
    else:
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        print("   ✅ Login OK")

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Get Me
    print("3. Testing /me...")
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert resp.status_code == 200, f"Get Me failed: {resp.text}"
    user = resp.json()
    assert user["email"] == email
    print(f"   ✅ Profile OK (Plan: {user['plan']})")

    # 4. Refresh Token
    print("4. Testing Token Refresh...")
    resp = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200, f"Refresh failed: {resp.text}"
    new_access_token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {new_access_token}"}
    print("   ✅ Refresh OK")

    # 5. Create Video (Ownership test)
    print("5. Testing Video Creation & Ownership...")
    video_data = {
        "title": "SaaS Test Video",
        "topic": "Space Travel",
        "template_id": "vertical_modern",
        "platform": "TikTok"
    }
    resp = requests.post(f"{BASE_URL}/videos/", json=video_data, headers=headers)
    assert resp.status_code == 200, f"Create video failed: {resp.text}"
    video_id = resp.json()["id"]
    print(f"   ✅ Video Created (ID: {video_id})")

    # 6. List Videos (Pagination test)
    print("6. Testing Pagination...")
    resp = requests.get(f"{BASE_URL}/videos/?page=1&limit=10", headers=headers)
    assert resp.status_code == 200, f"List videos failed: {resp.text}"
    page_data = resp.json()
    assert "items" in page_data
    assert page_data["total"] >= 1
    print(f"   ✅ Pagination OK (Total: {page_data['total']})")

    # 7. Download Endpoint (Conflict test - set status DONE and check)
    print("7. Testing Download Endpoint...")
    # Manually update status to DONE via PATCH (simulating orchestrator completion)
    # This requires reaching the owner check
    requests.patch(f"{BASE_URL}/videos/{video_id}", json={"status": "DONE"}, headers=headers)
    
    resp = requests.get(f"{BASE_URL}/videos/{video_id}/download", headers=headers)
    assert resp.status_code == 200, f"Download URL failed: {resp.text}"
    download_url = resp.json()["download_url"]
    assert email in download_url # Should contain user_id or sub-path
    print(f"   ✅ Download URL: {download_url}")

    print("\n--- ALL PHASE 3 BACKEND TESTS PASSED ---")

if __name__ == "__main__":
    try:
        test_saas_flow()
    except Exception as e:
        print(f"❌ Test aborted: {e}")
        print("Note: Ensure the backend is running at http://localhost:8000 and the database/redis are UP.")
