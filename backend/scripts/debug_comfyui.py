import requests, json, time

# 1. Aggressively free ALL VRAM
print("Unloading all models and freeing VRAM...")
r = requests.post("http://localhost:8188/free", json={"unload_models": True, "free_memory": True})
print(f"  /free response: {r.status_code}")
time.sleep(3)

# 2. Check system stats
r = requests.get("http://localhost:8188/system_stats")
stats = r.json()
for dev in stats.get("devices", []):
    total = dev.get("vram_total", 0) / 1024**3
    free = dev.get("vram_free", 0) / 1024**3
    name = dev.get("name", "unknown")
    print(f"  GPU: {name} | Total: {total:.1f}GB | Free: {free:.1f}GB")

# 3. Try a TINY 512x512 single image
print("Queueing a 512x512 test image...")
workflow = {
    "3": {"class_type": "KSampler", "inputs": {"cfg": 7, "denoise": 1, "latent_image": ["5", 0], "model": ["4", 0], "negative": ["7", 0], "positive": ["6", 0], "sampler_name": "euler", "scheduler": "normal", "seed": 999, "steps": 20}},
    "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"}},
    "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": 512, "width": 512}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "a cat sitting on a windowsill, soft lighting"}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "bad quality"}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "vram_test", "images": ["8", 0]}},
}
r = requests.post("http://localhost:8188/prompt", json={"prompt": workflow})
print(f"  Queue status: {r.status_code}")
prompt_id = r.json().get("prompt_id")
print(f"  prompt_id: {prompt_id}")

# 4. Wait for result
for i in range(120):
    h = requests.get(f"http://localhost:8188/history/{prompt_id}")
    data = h.json()
    if prompt_id in data:
        entry = data[prompt_id]
        status = entry.get("status", {})
        status_str = status.get("status_str", "unknown")
        print(f"  Status: {status_str}")
        if status_str == "error":
            for msg in status.get("messages", []):
                if isinstance(msg, list) and msg[0] == "execution_error":
                    print(f"  ERROR: {msg[1].get('exception_message', 'unknown')}")
        else:
            outputs = entry.get("outputs", {})
            for nid, nout in outputs.items():
                if "images" in nout:
                    print(f"  SUCCESS! Image: {nout['images'][0]['filename']}")
        break
    time.sleep(2)
    if i % 10 == 0:
        print(f"  ... waiting ({i*2}s)")
