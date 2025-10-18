# dependencies.py (or a new file, e.g., auth_dependencies.py)
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Missing environment variable: SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # login endpoint

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get the current user from JWT token.
    Raises 401 if token is invalid or missing.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Return user info (or load from DB if needed)
    return {"username": username}
