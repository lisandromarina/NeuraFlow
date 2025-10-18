from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class UserCredentialBase(BaseModel):
    user_id: int
    service: str
    auth_type: str
    credentials: str
    provider: Optional[str] = None  

class UserCredentialCreate(UserCredentialBase):
    pass

class UserCredentialUpdate(BaseModel):
    service: Optional[str] = None
    auth_type: Optional[str] = None
    credentials: Optional[str] = None

class UserCredentialSchema(UserCredentialBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserAuthentication(BaseModel):
    user_id: int
    service: str
    auth_type: str
    credentials: Dict
