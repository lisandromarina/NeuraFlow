from typing import List, Optional
from utils.token_security import decrypt_credentials
from models.db_models.user_credentials_db import UserCredentialDB
from models.schemas.user_credential import UserCredentialCreate, UserCredentialUpdate
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository

class UserCredentialService:
    def __init__(self, credential_repo: SqlAlchemyUserCredentialRepository):
        self.credential_repo = credential_repo

    def get_credential(self, credential_id: int) -> Optional[UserCredentialDB]:
        return self.credential_repo.get_by_id(credential_id)

    def list_credentials_by_user(self, user_id: int) -> List[UserCredentialDB]:
        return self.credential_repo.list_by_user(user_id)

    def create_credential(self, data: UserCredentialCreate) -> UserCredentialDB:
        new_cred = UserCredentialDB(**data.dict())
        return self.credential_repo.add(new_cred)

    def update_credential(self, credential_id: int, data: UserCredentialUpdate) -> Optional[UserCredentialDB]:
        cred = self.credential_repo.get_by_id(credential_id)
        if not cred:
            return None
        for field, value in data.dict(exclude_unset=True).items():
            setattr(cred, field, value)
        return self.credential_repo.update(cred)

    def delete_credential(self, credential_id: int) -> bool:
        return self.credential_repo.delete(credential_id)

    def get_credentials(self, user_id: int) -> Optional[dict]:
        """
        Fetch and decrypt the credentials for a given user_id.
        Returns the latest credential as a dictionary suitable for google.oauth2.credentials.Credentials.
        """
        creds_list = self.credential_repo.list_by_user(user_id)
        if not creds_list:
            return None

        # Pick the first (or latest) credential
        cred = creds_list[0]

        # Decrypt stored credentials JSON
        decrypted_creds = decrypt_credentials(cred.credentials)
        # Return in a standard format expected by your Google connectors
        return {
            "access_token": decrypted_creds.get("access_token"),
            "refresh_token": decrypted_creds.get("refresh_token"),
            "scope": decrypted_creds.get("scope"),
            "token_type": decrypted_creds.get("token_type"),
            "client_id": decrypted_creds.get("client_id"),
            "client_secret": decrypted_creds.get("client_secret"),
            "expires_in": decrypted_creds.get("expires_in"),
        }