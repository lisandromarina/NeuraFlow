from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .base import Base

class UserCredentialDB(Base):
    __tablename__ = "user_credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service = Column(String(100), nullable=False)         # e.g. "google_sheets", "facebook", "slack"
    auth_type = Column(String(50), nullable=False)        # e.g. "oauth2", "api_key", "service_account"
    credentials = Column(String, nullable=False)            # encrypted JSON payload
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("UserDB", back_populates="credentials")
