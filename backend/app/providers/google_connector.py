import os
import json
import base64
import requests
import urllib
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from typing import Dict, Any, Optional
from services.user_credential_service import UserCredentialService
from models.schemas.user_credential import UserAuthentication
from providers.base_credential_connector import BaseCredentialConnector


class GoogleConnector(BaseCredentialConnector):
    """Connector for Google OAuth2 authentication"""
    
    def connect(self, user_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OAuth URL for Google authentication"""
        provider = body["provider"]
        scopes = body["scopes"]
        provider_lower = provider.lower()

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        if not client_id:
            raise ValueError("Missing environment variable: GOOGLE_CLIENT_ID")
        if not redirect_uri:
            raise ValueError("Missing environment variable: GOOGLE_REDIRECT_URI")

        scope_str = " ".join(scopes)

        # Encode user_id in state
        state_payload = base64.urlsafe_b64encode(
            json.dumps({"user_id": user_id, "provider": provider_lower}).encode()
        ).decode()

        oauth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "access_type": "offline",
            "prompt": "consent",
            "state": state_payload
        })
        return {"oauth_url": oauth_url}
    
    def handle_callback(self, service_name: str, code: str, state: str) -> RedirectResponse:
        """Handle Google OAuth callback"""
        try:
            state_decoded = json.loads(base64.urlsafe_b64decode(state).decode())
            user_id = state_decoded["user_id"]
            provider = state_decoded.get("provider") 
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        token_endpoint = "https://oauth2.googleapis.com/token"
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        if not client_id:
            raise ValueError("Missing environment variable: GOOGLE_CLIENT_ID")
        if not client_secret:
            raise ValueError("Missing environment variable: GOOGLE_CLIENT_SECRET")
        if not redirect_uri:
            raise ValueError("Missing environment variable: GOOGLE_REDIRECT_URI")

        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        resp = requests.post(token_endpoint, data=data)

        if not resp.ok:
            raise HTTPException(status_code=400, detail="Failed to get tokens")

        token_data = resp.json()

        cred_data = {
            "user_id": user_id,
            "service": service_name,
            "auth_type": "oauth2",
            "credentials": token_data
        }

        self.credential_service.create_or_update_credential(UserAuthentication(**cred_data))

        # Redirect to frontend OAuth success page
        frontend_url = os.getenv("FRONTEND_URL")
        if not frontend_url:
            raise ValueError("Missing environment variable: FRONTEND_URL")
        frontend_url = frontend_url + "/oauth-success"
        query = urllib.parse.urlencode({"provider": provider})
        return RedirectResponse(f"{frontend_url}?{query}")

