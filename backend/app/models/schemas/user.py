# models/schemas/user.py
from pydantic import BaseModel, EmailStr # type: ignore
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    creation_date: datetime

    class Config:
        orm_mode = True
