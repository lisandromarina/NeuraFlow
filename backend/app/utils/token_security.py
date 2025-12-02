import json
from jose import jwe
from config import settings

# Get the decoded secret key (validation already done in Settings class)
SECRET_KEY = settings.credentials_secret_key_decoded

def encrypt_credentials(creds: dict) -> str:
    """Encrypt credentials JSON and return compact string"""
    # jwe.encrypt can return bytes, so decode to UTF-8
    encrypted = jwe.encrypt(json.dumps(creds), SECRET_KEY, algorithm='dir', encryption='A256GCM')
    if isinstance(encrypted, bytes):
        return encrypted.decode('utf-8')  # <-- return string
    return encrypted

def decrypt_credentials(encrypted: str) -> dict:
    """Decrypt credentials JSON"""
    decrypted = jwe.decrypt(encrypted, SECRET_KEY)
    return json.loads(decrypted)
