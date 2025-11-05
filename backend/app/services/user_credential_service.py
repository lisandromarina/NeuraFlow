import json
from typing import List, Optional
from utils.token_security import decrypt_credentials, encrypt_credentials
from models.db_models.user_credentials_db import UserCredentialDB
from models.schemas.user_credential import UserAuthentication, UserCredentialCreate, UserCredentialUpdate
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
    
    def get_credentials_by_service(self, user_id: int, service: str) -> Optional[dict]:
        """
        Fetch and decrypt credentials for a given user_id and service.
        Returns the decrypted credentials as a dictionary.
        """
        cred_db = self.credential_repo.get_by_user_and_service(user_id, service)
        if not cred_db:
            return None
        
        # Decrypt stored credentials JSON
        decrypted_creds = decrypt_credentials(cred_db.credentials)
        return decrypted_creds
    
    def create_or_update_credential(self, data: UserAuthentication) -> UserCredentialDB:
        """
        Creates or updates a credential for a user:
        - For OAuth services: Merges scopes if new ones are provided
        - For API key services: Replaces the existing credentials
        - Otherwise, creates a new credential entry (encrypted).
        """
        existing_cred: UserCredentialDB = self.credential_repo.get_by_user_and_service(
            user_id=data.user_id, service=data.service
        )

        if existing_cred:
            # Handle OAuth (with scopes) vs API key (without scopes)
            if data.auth_type == "oauth2" and "scope" in data.credentials:
                existing_data = decrypt_credentials(existing_cred.credentials)

                existing_scopes = set(existing_data.get("scope", "").split())
                new_scopes = set(data.credentials.get("scope", "").split())

                if new_scopes.issubset(existing_scopes):
                    return existing_cred

                # Merge scopes for OAuth
                merged_scopes = list(existing_scopes.union(new_scopes))
                existing_data["scope"] = " ".join(merged_scopes)

                # Update existing credential with merged scopes
                updated_encrypted = encrypt_credentials(existing_data)
                existing_cred.credentials = updated_encrypted

                return self.credential_repo.update(existing_cred)
            else:
                # For API keys or other auth types, just replace the credentials
                updated_encrypted = encrypt_credentials(data.credentials)
                existing_cred.credentials = updated_encrypted
                existing_cred.auth_type = data.auth_type

                return self.credential_repo.update(existing_cred)

        # ✅ Create new credential (encrypt credentials first)
        encrypted_creds = encrypt_credentials(data.credentials)
        new_cred = UserCredentialDB(
            user_id=data.user_id,
            service=data.service,
            auth_type=data.auth_type,
            credentials=encrypted_creds
        )

        print("Creating new credential for service:", data.service)
        return self.credential_repo.add(new_cred)