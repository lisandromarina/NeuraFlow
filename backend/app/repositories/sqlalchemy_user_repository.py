# repositories/sqlalchemy_user_repository.py
from sqlalchemy.orm import Session # type: ignore
from models.db_models.user_db import UserDB
from utils.security import hash_password

class SqlAlchemyUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(UserDB).filter(UserDB.email == email).first()

    def create_user(self, email: str, password: str):
        hashed_pw = hash_password(password)
        user = UserDB(email=email, password=hashed_pw)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
