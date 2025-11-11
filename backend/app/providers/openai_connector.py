from fastapi import HTTPException
from typing import Dict, Any
from services.user_credential_service import UserCredentialService
from models.schemas.user_credential import UserAuthentication
from providers.base_credential_connector import BaseCredentialConnector


class OpenAIConnector(BaseCredentialConnector):
    """Connector for OpenAI API key authentication"""
    
    def connect(self, user_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
        """Store OpenAI API key directly"""
        api_key = body.get("api_key")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="Missing 'api_key' in request body")

        # Store the API key encrypted as user credentials
        cred_data = {
            "user_id": user_id,
            "service": "openai",
            "auth_type": "api_key",
            "credentials": {"api_key": api_key}
        }

        self.credential_service.create_or_update_credential(UserAuthentication(**cred_data))
        
        return {"status": "success", "message": "OpenAI API key stored successfully"}
    
    def handle_callback(self, service_name: str, code: str, state: str) -> None:
        """OpenAI doesn't use OAuth callbacks"""
        return None

