import httpx

for url in ['http://127.0.0.1:8188/system_stats', 'http://127.0.0.1:7861/sdapi/v1/options']:
    try:
        r = httpx.get(url, timeout=3.0)
        print(url, '->', r.status_code)
    except Exception as e:
        print(url, 'unreachable:', e)
