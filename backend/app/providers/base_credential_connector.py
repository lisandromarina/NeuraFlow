from abc import ABC, abstractmethod
from typing import Dict, Any
from services.user_credential_service import UserCredentialService


class BaseCredentialConnector(ABC):
    """Base class for credential connectors"""
    
    def __init__(self, credential_service: UserCredentialService):
        self.credential_service = credential_service
    
    @abstractmethod
    def connect(self, user_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the connection process for a service.
        Returns a dict with connection details (e.g., oauth_url or success message).
        """
        pass
    
    @abstractmethod
    def handle_callback(self, service_name: str, code: str, state: str) -> Any:
        """
        Handle OAuth callback (if applicable).
        Returns redirect response or None for API key services.
        """
        pass

