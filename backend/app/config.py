"""
Configuration management using pydantic-settings.

This module provides centralized configuration management with validation
for all environment variables used throughout the application.
"""
import base64
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and defaults."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars
    )
    
    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL database connection URL"
    )
    
    # Redis Configuration
    redis_url: str = Field(
        ...,
        description="Redis connection URL"
    )
    
    # JWT Authentication
    secret_key: str = Field(
        ...,
        description="JWT signing secret key"
    )
    
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="JWT access token expiration time in minutes"
    )
    
    # Credentials Encryption
    credentials_secret_key: str = Field(
        ...,
        description="Base64-encoded 32-byte key for credential encryption"
    )
    
    @field_validator("credentials_secret_key")
    @classmethod
    def validate_credentials_secret_key(cls, v: str) -> str:
        """Validate that credentials secret key decodes to exactly 32 bytes."""
        try:
            decoded = base64.urlsafe_b64decode(v)
            if len(decoded) != 32:
                raise ValueError(
                    "CREDENTIALS_SECRET_KEY must decode to exactly 32 bytes for A256GCM encryption"
                )
        except Exception as e:
            if isinstance(e, ValueError) and "32 bytes" in str(e):
                raise
            raise ValueError(
                f"CREDENTIALS_SECRET_KEY must be a valid base64-encoded string: {e}"
            )
        return v
    
    # Google OAuth Configuration
    google_client_id: str = Field(
        ...,
        description="Google OAuth client ID"
    )
    
    google_client_secret: str = Field(
        ...,
        description="Google OAuth client secret"
    )
    
    google_redirect_uri: str = Field(
        ...,
        description="Google OAuth redirect URI for credentials connection"
    )
    
    google_auth_redirect_uri: Optional[str] = Field(
        default=None,
        description="Google OAuth redirect URI for user authentication"
    )
    
    # Frontend Configuration
    frontend_url: str = Field(
        ...,
        description="Frontend application URL for CORS and redirects"
    )
    
    # Optional Configuration
    ngrok_url: Optional[str] = Field(
        default=None,
        description="Ngrok public URL for Telegram webhooks"
    )
    
    db_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging (useful for debugging)"
    )
    
    @property
    def allowed_origins(self) -> list[str]:
        """Parse FRONTEND_URL to support multiple comma-separated origins."""
        if not self.frontend_url:
            return []
        origins = [
            origin.strip() 
            for origin in self.frontend_url.split(",") 
            if origin.strip()
        ]
        return origins
    
    @property
    def credentials_secret_key_decoded(self) -> bytes:
        """Get the decoded credentials secret key."""
        return base64.urlsafe_b64decode(self.credentials_secret_key)


# Global settings instance
# This will be instantiated when the module is imported and will validate
# all environment variables on startup
settings = Settings()


