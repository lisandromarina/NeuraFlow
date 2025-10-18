from typing import List, Optional
from sqlalchemy.orm import Session
from models.db_models.user_credentials_db import UserCredentialDB

class SqlAlchemyUserCredentialRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, credential_id: int) -> Optional[UserCredentialDB]:
        return self.db.query(UserCredentialDB).filter(UserCredentialDB.id == credential_id).first()

    def list_by_user(self, user_id: int) -> List[UserCredentialDB]:
        return self.db.query(UserCredentialDB).filter(UserCredentialDB.user_id == user_id).all()

    def add(self, credential: UserCredentialDB) -> UserCredentialDB:
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def update(self, credential: UserCredentialDB) -> UserCredentialDB:
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def delete(self, credential_id: int) -> bool:
        credential = self.get_by_id(credential_id)
        if not credential:
            return False
        self.db.delete(credential)
        self.db.commit()
        return True
    
    def get_by_user_and_service(self, user_id: int, service: str) -> UserCredentialDB:
        return (
            self.db.query(UserCredentialDB)
            .filter(UserCredentialDB.user_id == user_id)
            .filter(UserCredentialDB.service == service)
            .first()
        )
