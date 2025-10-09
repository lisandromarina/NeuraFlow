# models/db_models/user_db.py
from sqlalchemy import Column, Integer, String, DateTime # type: ignore
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # hashed password
    creation_date = Column(DateTime, default=datetime.utcnow)

    workflows = relationship("WorkflowDB", back_populates="user", cascade="all, delete-orphan")

