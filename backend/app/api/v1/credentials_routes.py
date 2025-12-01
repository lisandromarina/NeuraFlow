from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from typing import List
from models.schemas.user_credential import (
    UserCredentialCreate,
    UserCredentialUpdate,
    UserCredentialSchema,
)
from services.user_credential_service import UserCredentialService
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from dependencies import get_user_credential_repository, get_db_session
from providers.credential_connector_factory import CredentialConnectorFactory
from auth_dependencies import get_current_user, verify_credential_ownership
from sqlalchemy.orm import Session # type: ignore

router = APIRouter(prefix="/credentials", tags=["User Credentials"])

# ---------------- Dependency ----------------

def get_user_credential_service(
    repo: SqlAlchemyUserCredentialRepository = Depends(get_user_credential_repository)
) -> UserCredentialService:
    return UserCredentialService(repo)

# ---------------- CRUD ROUTES ----------------

@router.get("/{credential_id}", response_model=UserCredentialSchema)
def get_credential(
    credential_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: UserCredentialService = Depends(get_user_credential_service)
):
    """Get a credential (requires ownership)"""
    # Verify ownership
    verify_credential_ownership(credential_id, current_user, db)
    
    cred = service.get_credential(credential_id)
    if not cred:
        raise HTTPException(status_code=404, detail="Credential not found")
    return cred

@router.get("/user/{user_id}", response_model=List[UserCredentialSchema])
def list_credentials(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    service: UserCredentialService = Depends(get_user_credential_service)
):
    """List credentials for a user (users can only access their own credentials)"""
    # Ensure user can only access their own credentials
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own credentials")
    
    return service.list_credentials_by_user(user_id)

@router.post("/", response_model=UserCredentialSchema)
def create_credential(
    data: UserCredentialCreate,
    current_user: dict = Depends(get_current_user),
    service: UserCredentialService = Depends(get_user_credential_service)
):
    """Create a credential for the current user"""
    # Ensure user_id matches current user
    data.user_id = current_user["user_id"]
    return service.create_credential(data)

@router.put("/{credential_id}", response_model=UserCredentialSchema)
def update_credential(
    credential_id: int,
    data: UserCredentialUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: UserCredentialService = Depends(get_user_credential_service)
):
    """Update a credential (requires ownership)"""
    # Verify ownership
    verify_credential_ownership(credential_id, current_user, db)
    
    updated = service.update_credential(credential_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Credential not found")
    return updated

@router.delete("/{credential_id}", response_model=dict)
def delete_credential(
    credential_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: UserCredentialService = Depends(get_user_credential_service)
):
    """Delete a credential (requires ownership)"""
    # Verify ownership
    verify_credential_ownership(credential_id, current_user, db)
    
    deleted = service.delete_credential(credential_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Credential not found")
    return {"deleted": True}

# ---------------- OAUTH CONNECT FLOW ----------------

def get_connector_factory(
    credential_service: UserCredentialService = Depends(get_user_credential_service)
) -> CredentialConnectorFactory:
    """Dependency to get credential connector factory"""
    return CredentialConnectorFactory(credential_service)

@router.post("/{service}/connect")
def connect_service(
    service: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
    factory: CredentialConnectorFactory = Depends(get_connector_factory)
):
    """
    Connect a service account:
    - For OAuth services (like Google): Generate OAuth URL
    - For API key services (like OpenAI): Accept and store API key directly
    """
    # Ensure user_id matches current user
    if "user_id" in body and body["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You can only connect services for yourself")
    
    user_id = current_user["user_id"]
    body["user_id"] = user_id
    
    connector = factory.get_connector(service)
    if not connector:
        raise HTTPException(status_code=400, detail=f"Unsupported service: {service}")
    
    return connector.connect(user_id, body)

@router.get("/callback/{service_name}")
def oauth_callback(
    service_name: str,
    code: str = Query(...),
    state: str = Query(...),
    factory: CredentialConnectorFactory = Depends(get_connector_factory)
):
    """Handle OAuth callback for supported services"""
    connector = factory.get_connector(service_name)
    if not connector:
        raise HTTPException(status_code=400, detail=f"Unsupported service: {service_name}")
    
    result = connector.handle_callback(service_name, code, state)
    if result is None:
        raise HTTPException(status_code=400, detail=f"Service {service_name} does not support OAuth callbacks")
    
    return result

