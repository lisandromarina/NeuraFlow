from typing import Optional
from services.user_credential_service import UserCredentialService
from providers.base_credential_connector import BaseCredentialConnector
from providers.openai_connector import OpenAIConnector
from providers.google_connector import GoogleConnector


class CredentialConnectorFactory:
    """Factory for creating credential connectors"""
    
    def __init__(self, credential_service: UserCredentialService):
        self.credential_service = credential_service
        self._connectors = {
            "openai": OpenAIConnector(credential_service),
            "google": GoogleConnector(credential_service),
        }
    
    def get_connector(self, service: str) -> Optional[BaseCredentialConnector]:
        """
        Get the connector for a given service.
        Returns None if service is not supported.
        """
        service_lower = service.lower()
        return self._connectors.get(service_lower)

