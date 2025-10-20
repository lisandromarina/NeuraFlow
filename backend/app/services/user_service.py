# services/user_service.py
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from utils.security import verify_password, hash_password
from models.db_models.user_db import UserDB
from models.schemas.workflow import Workflow
from fastapi import HTTPException
from typing import Optional

class UserService:
    def __init__(
        self, 
        user_repo: SqlAlchemyUserRepository, 
        workflow_repo: Optional[SqlAlchemyWorkflowRepository] = None
    ):
        self.user_repo = user_repo
        self.workflow_repo = workflow_repo

    def register_user(self, email: str, password: str) -> UserDB:
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create the user
        user = self.user_repo.create_user(email, password)
        
        # Create a default workflow for the new user
        if self.workflow_repo:
            default_workflow = Workflow(
                name="My First Workflow",
                description="Welcome! This is your default workflow to get started.",
                user_id=user.id
            )
            self.workflow_repo.add(default_workflow)
        
        return user

    def authenticate_user(self, email: str, password: str) -> UserDB:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return user

    def get_user_by_email(self, email: str) -> UserDB | None:
        return self.user_repo.get_by_email(email)