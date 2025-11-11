from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from typing import List
from models.schemas.user_credential import (
    UserCredentialCreate,
    UserCredentialUpdate,
    UserCredentialSchema,
)
from services.user_credential_service import UserCredentialService
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from dependencies import get_user_credential_repository
from providers.credential_connector_factory import CredentialConnectorFactory

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

def get_connector_factory(
    credential_service: UserCredentialService = Depends(get_user_credential_service)
) -> CredentialConnectorFactory:
    """Dependency to get credential connector factory"""
    return CredentialConnectorFactory(credential_service)

@router.post("/{service}/connect")
def connect_service(
    service: str, 
    body: dict,
    factory: CredentialConnectorFactory = Depends(get_connector_factory)
):
    """
    Connect a service account:
    - For OAuth services (like Google): Generate OAuth URL
    - For API key services (like OpenAI): Accept and store API key directly
    """
    user_id = body["user_id"]
    
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

