# services/user_service.py
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from utils.security import verify_password, hash_password
from models.db_models.user_db import UserDB
from fastapi import HTTPException
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, user_repo: SqlAlchemyUserRepository):
        self.user_repo = user_repo

    def register_user(self, email: str, password: str) -> UserDB:
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        return self.user_repo.create_user(email, password)

    def authenticate_user(self, email: str, password: str) -> UserDB:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return user

    def get_user_by_email(self, email: str) -> UserDB | None:
        return self.user_repo.get_by_email(email)