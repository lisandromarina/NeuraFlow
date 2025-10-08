from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Create a password hasher instance
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """
    Hashes a password using Argon2.
    No 72-byte limit like bcrypt.
    """
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a hashed password.
    Returns True if matches, False otherwise.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
