import base64
import os
import json
from jose import jwe

# Load secret key from env and decode from Base64
SECRET_KEY_B64 = os.getenv("CREDENTIALS_SECRET_KEY")
if not SECRET_KEY_B64:
    raise ValueError("Missing environment variable: CREDENTIALS_SECRET_KEY")

SECRET_KEY = base64.urlsafe_b64decode(SECRET_KEY_B64)

# Make sure the key is exactly 32 bytes
if len(SECRET_KEY) != 32:
    raise ValueError("CREDENTIALS_SECRET_KEY must decode to exactly 32 bytes for A256GCM")

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
