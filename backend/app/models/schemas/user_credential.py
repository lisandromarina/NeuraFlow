from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class UserCredentialBase(BaseModel):
    user_id: int
    service: str
    auth_type: str
    credentials: str  

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
