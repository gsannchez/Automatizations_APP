import requests, time

for i in range(10):
    try:
        r = requests.get("http://localhost:8188/system_stats", timeout=5)
        d = r.json()
        print("ComfyUI is UP")
        for x in d.get("devices", []):
            name = x.get("name", "?")
            total = x.get("vram_total", 0) / 1024**3
            free = x.get("vram_free", 0) / 1024**3
            print(f"  GPU: {name} | Total: {total:.1f}GB | Free: {free:.1f}GB")
        break
    except Exception:
        print(f"  Waiting for ComfyUI... ({i+1})")
        time.sleep(3)
