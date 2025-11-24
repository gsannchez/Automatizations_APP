import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Obtener clave de encriptación desde variable de entorno
# En producción, esto debería estar en un servicio de secretos como AWS KMS
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Generar una nueva clave si no existe (solo para desarrollo)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"⚠️  Generated new encryption key: {ENCRYPTION_KEY}")
    print("⚠️  Add this to your .env file as ENCRYPTION_KEY")

fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_token(token: str) -> str:
    """Encripta un token OAuth."""
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Desencripta un token OAuth."""
    return fernet.decrypt(encrypted_token.encode()).decode()
