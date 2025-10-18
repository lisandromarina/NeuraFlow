import urllib
from utils.token_security import encrypt_credentials
from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from fastapi.responses import RedirectResponse # type: ignore
from typing import List
from urllib.parse import urlencode
import os, json, base64, requests
from models.schemas.user_credential import (
    UserAuthentication,
    UserCredentialCreate,
    UserCredentialUpdate,
    UserCredentialSchema,
)
from services.user_credential_service import UserCredentialService
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from dependencies import get_user_credential_repository

router = APIRouter(prefix="/credentials", tags=["User Credentials"])

# ---------------- Dependency ----------------

def get_user_credential_service(
    repo: SqlAlchemyUserCredentialRepository = Depends(get_user_credential_repository)
) -> UserCredentialService:
    return UserCredentialService(repo)

# ---------------- CRUD ROUTES ----------------

@router.get("/{credential_id}", response_model=UserCredentialSchema)
def get_credential(credential_id: int, service: UserCredentialService = Depends(get_user_credential_service)):
    cred = service.get_credential(credential_id)
    if not cred:
        raise HTTPException(status_code=404, detail="Credential not found")
    return cred

@router.get("/user/{user_id}", response_model=List[UserCredentialSchema])
def list_credentials(user_id: int, service: UserCredentialService = Depends(get_user_credential_service)):
    return service.list_credentials_by_user(user_id)

@router.post("/", response_model=UserCredentialSchema)
def create_credential(data: UserCredentialCreate, service: UserCredentialService = Depends(get_user_credential_service)):
    return service.create_credential(data)

@router.put("/{credential_id}", response_model=UserCredentialSchema)
def update_credential(
    credential_id: int,
    data: UserCredentialUpdate,
    service: UserCredentialService = Depends(get_user_credential_service)
):
    updated = service.update_credential(credential_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Credential not found")
    return updated

@router.delete("/{credential_id}", response_model=dict)
def delete_credential(credential_id: int, service: UserCredentialService = Depends(get_user_credential_service)):
    deleted = service.delete_credential(credential_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Credential not found")
    return {"deleted": True}

# ---------------- OAUTH CONNECT FLOW ----------------

@router.post("/{service}/connect")
def connect_service(service: str, body: dict):
    """
    Generate OAuth URL for the user to connect their account.
    Encodes user_id in the state parameter for safe identification.
    """
    user_id = body["user_id"]
    provider = body["provider"]
    scopes = body["scopes"]

    service_lower = service.lower()
    provider_lower = provider.lower()

    if service_lower.lower() == "google":

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/credentials/callback/google"
        )

        scope_str = " ".join(scopes)

        # Encode user_id in state
        state_payload = base64.urlsafe_b64encode(
            json.dumps({"user_id": user_id, "provider": provider_lower}).encode()
        ).decode()

        oauth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "access_type": "offline",
            "prompt": "consent",
            "state": state_payload
        })
        return {"oauth_url": oauth_url}

    raise HTTPException(status_code=400, detail="Unsupported service")

@router.get("/callback/{service_name}")
def oauth_callback(
    service_name: str,
    code: str = Query(...),
    state: str = Query(...),
    service: UserCredentialService = Depends(get_user_credential_service)
):
    try:
        state_decoded = json.loads(base64.urlsafe_b64decode(state).decode())
        user_id = state_decoded["user_id"]
        provider = state_decoded.get("provider") 
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    if service_name.lower() == "google":
        token_endpoint = "https://oauth2.googleapis.com/token"
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/credentials/callback/google_sheets"
        )

        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        resp = requests.post(token_endpoint, data=data)

        if not resp.ok:
            raise HTTPException(status_code=400, detail="Failed to get tokens")

        token_data = resp.json()

        cred_data = {
            "user_id": user_id,
            "service": service_name,
            "auth_type": "oauth2",
            "credentials": token_data
        }

        service.create_or_update_credential(UserAuthentication(**cred_data))

        # Redirect to frontend OAuth success page
        frontend_url = "http://localhost:3000/oauth-success"
        query = urllib.parse.urlencode({"provider": provider})
        return RedirectResponse(f"{frontend_url}?{query}")
