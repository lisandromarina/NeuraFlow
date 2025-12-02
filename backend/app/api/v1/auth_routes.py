# api/v1/auth_routes.py
from http.client import HTTPException
from fastapi import APIRouter, Depends, HTTPException, Header # type: ignore
from fastapi.responses import RedirectResponse # type: ignore
from dependencies import get_user_repository, get_workflow_repository
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from services.user_service import UserService
from models.schemas.user import UserCreate, UserRead
from datetime import datetime, timedelta
from jose import jwt, JWTError # type: ignore
from urllib.parse import urlencode
import requests
from config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Use the repository dependency you already defined
def get_user_service(
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
    workflow_repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)
) -> UserService:
    return UserService(user_repo, workflow_repo)

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, service: UserService = Depends(get_user_service)):
    return service.register_user(user.email, user.password)

@router.post("/login")
def login(user: UserCreate, service: UserService = Depends(get_user_service)):
    db_user = service.authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": db_user.email,
        "user_id": db_user.id, 
        "exp": expire
    }

    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/validate-token")
def validate_token(authorization: str = Header(...)):
    """
    Validates the provided JWT access token.
    Returns success if still valid, otherwise raises 401.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp = payload.get("exp")

        if exp is None or datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")

        return {"valid": True, "email": payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------- GOOGLE OAUTH LOGIN ----------------

@router.get("/google/login")
def google_login():
    """
    Initiates Google OAuth flow for user authentication.
    Redirects to Google OAuth consent screen.
    """
    client_id = settings.google_client_id
    redirect_uri = settings.google_auth_redirect_uri or "http://localhost:8000/auth/google/callback"
    
    # Basic scopes for authentication (email and profile)
    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    
    oauth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "access_type": "online",
        "prompt": "select_account"
    })
    
    return RedirectResponse(oauth_url)

@router.get("/google/callback")
def google_callback(code: str, service: UserService = Depends(get_user_service)):
    """
    Handles Google OAuth callback.
    Exchanges code for tokens, gets user info, creates/authenticates user.
    """
    client_id = settings.google_client_id
    client_secret = settings.google_client_secret
    redirect_uri = settings.google_auth_redirect_uri or "http://localhost:8000/auth/google/callback"
    
    # Exchange code for tokens
    token_endpoint = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    token_response = requests.post(token_endpoint, data=token_data)
    if not token_response.ok:
        raise HTTPException(status_code=400, detail="Failed to get tokens from Google")
    
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    
    # Get user info from Google
    userinfo_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(userinfo_endpoint, headers=headers)
    
    if not userinfo_response.ok:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    
    user_info = userinfo_response.json()
    email = user_info.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")
    
    # Check if user exists, if not create them
    db_user = service.get_user_by_email(email)
    if not db_user:
        # Register new user with a random password (they'll use Google to login)
        import secrets
        random_password = secrets.token_urlsafe(32)
        db_user = service.register_user(email, random_password)
    
    # Generate JWT token
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": db_user.email,
        "user_id": db_user.id,
        "exp": expire
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    
    # Redirect to frontend workflow page with token
    frontend_url = settings.frontend_url.split(",")[0].strip()  # Use first URL if multiple
    return RedirectResponse(f"{frontend_url}/oauth-success?token={token}")
