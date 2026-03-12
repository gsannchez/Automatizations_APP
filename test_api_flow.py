import time
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_api_flow():
    print("🚀 Iniciando prueba completa del flujo de la API...")
    
    # 1. Verificar que el servidor está corriendo
    try:
        requests.get("http://localhost:8000/docs", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Error: El servidor backend no parece estar corriendo en http://localhost:8000")
        print("   Por favor inicia el servidor y asegúrate de que Celery y Redis también estén activos.")
        sys.exit(1)

    # 2. Crear Template
    template_data = {
        "name": "Template de Prueba API",
        "platform": "TIKTOK",
        "description": "Plantilla temporal para testing del flujo de video",
        "structure_json": '[{"duration": 5, "type": "intro"}, {"duration": 5, "type": "main"}]'
    }
    r = requests.post(f"{BASE_URL}/templates/", json=template_data)
    r.raise_for_status()
    template_id = r.json()["id"]
    print(f"✅ Template creado con UUID: {template_id}")

    # 3. Crear Registro de Video
    print("\n2️⃣ Registrando Video en la base de datos...")
    video_data = {
        "title": "Prueba End-to-End",
        "topic": "Inteligencia Artificial 2026",
        "platform": "TIKTOK",
        "template_id": template_id
    }
    r = requests.post(f"{BASE_URL}/videos/", json=video_data)
    r.raise_for_status()
    video_id = r.json()["id"]
    print(f"✅ Video registrado con UUID: {video_id}")

    # 4. Encolar Generación (Celery Orchestrator)
    print("\n3️⃣ Solicitando inicio de generación (Orquestador)...")
    r = requests.post(f"{BASE_URL}/videos/{video_id}/generate")
    r.raise_for_status()
    print("✅ Tarea enviada a Celery correctamente")

    # 5. Monitorear Progreso a través de Polling
    print("\n4️⃣ Monitoreando progreso (Polling status)...")
    attempts = 0
    max_attempts = 120  # 120 * 5s = 10 minutos máximo

    while attempts < max_attempts:
        r = requests.get(f"{BASE_URL}/videos/{video_id}/status")
        
        if r.status_code != 200:
            print(f"❌ Error al consultar status: {r.text}")
            break
            
        status_data = r.json()
        current_status = status_data.get('status', 'UNKNOWN')
        progress = status_data.get('progress', 0)
        
        bar_length = 30
        filled = int(bar_length * progress // 100)
        bar = '█' * filled + '-' * (bar_length - filled)
        
        print(f"\rProgreso: [{bar}] {progress}% | Estado: {current_status}", end="", flush=True)
        
        if current_status == "DONE":
            print("\n\n🎉 ¡Flujo completado exitosamente!")
            
            # Obtener datos finales del video
            r_final = requests.get(f"{BASE_URL}/videos/{video_id}")
            if r_final.status_code == 200:
                final_data = r_final.json()
                print(f"📁 Archivo final en Storage Key: {final_data.get('storage_key')}")
            break
        elif current_status == "FAILED":
            print("\n\n❌ El proceso ha fallado.")
            # Obtener detalles del error
            r_error = requests.get(f"{BASE_URL}/videos/{video_id}")
            if r_error.status_code == 200:
                error_data = r_error.json()
                print(f"Paso del error: {error_data.get('error_step')}")
                print(f"Mensaje de error: {error_data.get('error_message')}")
            break
            
        time.sleep(5)
        attempts += 1
        
    if attempts >= max_attempts:
        print("\n\n⏱️ Timeout alcanzado esperando que termine el video.")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ El módulo 'requests' no está instalado. Instalando temporalmente...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests

    test_api_flow()
