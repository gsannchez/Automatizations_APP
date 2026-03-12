import httpx
import time
import sys
import os
from uuid import UUID

# This script assumes the backend is running at http://localhost:8000
BASE_URL = "http://localhost:8000/api/v1"

def run_e2e_test():
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)
    
    email = f"e2e_{int(time.time())}@example.com"
    password = "SecurePassword123"
    
    print(f"--- Phase 1: User Onboarding ({email}) ---")
    reg_resp = client.post("/auth/register", json={"email": email, "password": password})
    if reg_resp.status_code != 201:
        print(f"FAILED: Registration returned {reg_resp.status_code}")
        return False
    
    login_resp = client.post("/auth/login", json={"email": email, "password": password})
    tokens = login_resp.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("SUCCESS: Logged in and received JWT.")

    print("\n--- Phase 2: Video Initialization ---")
    # Using a dummy UUID for template in this simulation
    create_resp = client.post("/videos/", json={
        "title": "E2E Automated Test Video",
        "template_id": "00000000-0000-0000-0000-000000000000",
        "platform": "TIKTOK",
        "topic": "The future of automation"
    }, headers=headers)
    video = create_resp.json()
    video_id = video["id"]
    print(f"SUCCESS: Created video record ID: {video_id}")

    print("\n--- Phase 3: Trigger Generation ---")
    gen_resp = client.post(f"/videos/{video_id}/generate", headers=headers)
    if gen_resp.status_code == 200:
        print("SUCCESS: Generation task queued in Celery.")
    else:
        print(f"WARNING: Trigger returned {gen_resp.status_code}. Celery might not be reachable.")

    print("\n--- Phase 4: Status Polling ---")
    max_attempts = 120 # 2 minutes
    completed = False
    
    # Note: For the sake of the test script, if the worker isn't running, we won't wait forever.
    # We poll a few times to show logic.
    for i in range(max_attempts):
        status_resp = client.get(f"/videos/{video_id}/status", headers=headers)
        status_data = status_resp.json()
        status = status_data["status"]
        
        print(f"Step {i+1}: Current Status = {status}")
        
        if status == "DONE":
            completed = True
            break
        elif status == "FAILED":
            print(f"ERROR: Video failed at step {status_data.get('error_step')}: {status_data.get('error_message')}")
            return False
        
        time.sleep(2)
    
    if not completed:
        print("TIMEOUT: Video generation did not complete within 2 minutes. (Check if Celery worker is running)")
        # We continue to test the download logic anyway (mocking it if needed)
        return False

    print("\n--- Phase 5: Download Verification ---")
    dl_resp = client.get(f"/videos/{video_id}/download", headers=headers)
    if dl_resp.status_code == 200:
        download_url = dl_resp.json()["download_url"]
        print(f"SUCCESS: Download URL generated: {download_url}")
        return True
    else:
        print(f"FAILED: Could not get download URL (Status: {dl_resp.status_code})")
        return False

if __name__ == "__main__":
    success = run_e2e_test()
    if success:
        print("\n" + "="*40)
        print("   ✅ FULL E2E WORKFLOW SUCCESSFUL   ")
        print("="*40)
        sys.exit(0)
    else:
        print("\n" + "="*40)
        print("   ❌ E2E WORKFLOW FAILED          ")
        print("="*40)
        sys.exit(1)
