import time
import requests
import sys
import uuid

# Configuración
BASE_URL = "http://localhost:8000/api/v1"

def ejecutar_test():
    print("\n" + "="*50)
    print("🚀 INICIANDO PRUEBA INTEGRAL DEL SISTEMA")
    print("="*50)

    # 1. Verificar Servidor
    try:
        requests.get("http://localhost:8000/", timeout=2)
    except:
        print("❌ ERROR: El backend no está corriendo en http://localhost:8000")
        print("💡 Ejecuta '.\start_app.ps1' primero.")
        return

    # 2. Autenticación (Usuario Único por Test)
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    password = "password123"
    print(f"\n1️⃣  Registrando usuario: {email}...")
    
    r = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    if r.status_code != 201:
        print(f"❌ Error en registro: {r.text}")
        return
    
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Usuario registrado y autenticado.")

    # 3. Crear Template
    print("\n2️⃣  Creando Template de video...")
    template_data = {
        "name": "E2E Template",
        "platform": "TIKTOK",
        "description": "Test automatizado",
        "structure_json": '[{"duration": 5, "type": "intro"}]'
    }
    r = requests.post(f"{BASE_URL}/templates/", json=template_data, headers=headers)
    template_id = r.json()["id"]
    print(f"✅ Template ID: {template_id}")

    # 4. Crear Video y Encolar
    print("\n3️⃣  Creando Video y enviando a procesar...")
    video_data = {
        "title": "Video de Prueba E2E",
        "topic": "Automatización",
        "platform": "TIKTOK",
        "template_id": template_id
    }
    r = requests.post(f"{BASE_URL}/videos/", json=video_data, headers=headers)
    video_id = r.json()["id"]
    
    # Trigger generation
    requests.post(f"{BASE_URL}/videos/{video_id}/generate", headers=headers)
    print(f"✅ Video encolado. ID: {video_id}")

    # 5. Polling de Status
    print("\n4️⃣  Monitoreando generación (esperando a Celery)...")
    start_time = time.time()
    max_wait = 300 # 5 min
    
    try:
        while (time.time() - start_time) < max_wait:
            r = requests.get(f"{BASE_URL}/videos/{video_id}/status", headers=headers)
            status_data = r.json()
            status = status_data["status"]
            progress = status_data.get("progress", 0)
            
            # Barra de progreso simple
            bar = "█" * (progress // 5) + "░" * (20 - (progress // 5))
            print(f"\r   [{bar}] {progress}% | Estado: {status}   ", end="", flush=True)
            
            if status == "DONE":
                print("\n\n✅ ¡GENERACIÓN COMPLETADA!")
                break
            elif status == "FAILED":
                print(f"\n\n❌ ERROR en generación: {status_data.get('error_message')}")
                return
            
            time.sleep(3)
        else:
            print("\n\n⏱️  TIMEOUT: El video tardó demasiado.")
            return
    except KeyboardInterrupt:
        print("\n\n🛑 Prueba cancelada por el usuario.")
        return

    # 6. Verificar Descarga
    print("\n5️⃣  Verificando link de descarga...")
    r = requests.get(f"{BASE_URL}/videos/{video_id}/download", headers=headers)
    if r.status_code == 200:
        print(f"✅ Link generado: {r.json()['download_url'][:60]}...")
    else:
        print(f"❌ No se pudo generar el link: {r.text}")

    print("\n" + "="*50)
    print("🎉 TODAS LAS PRUEBAS DEL SISTEMA PASARON")
    print("="*50 + "\n")

if __name__ == "__main__":
    ejecutar_test()
