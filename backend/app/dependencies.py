from fastapi import Depends # type: ignore
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from repositories.sqlalchemy_workflow_connection_repository import SqlAlchemyWorkflowConnectionRepository
from models.db_models.workflow_db import Base
from redis import Redis # type: ignore
from config import settings

# 1. Create engine and session
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,  # Disable in production, enable via DB_ECHO=true env var for development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 2. Create tables
Base.metadata.create_all(engine)

# 3. DB session dependency
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Repository provider (after get_db_session is defined)
def get_workflow_repository(db = Depends(get_db_session)):
    yield SqlAlchemyWorkflowRepository(db)

def get_node_repository(db = Depends(get_db_session)):
    return SqlAlchemyNodeRepository(db)

def get_workflow_node_repository(db = Depends(get_db_session)):
    return SqlAlchemyWorkflowNodeRepository(db)

def get_user_repository(db = Depends(get_db_session)):
    return SqlAlchemyUserRepository(db)

def get_user_credential_repository(db=Depends(get_db_session)):
    """Provides User Credential repository dependency"""
    return SqlAlchemyUserCredentialRepository(db)

def get_workflow_connection_repository(db=Depends(get_db_session)):
    """Provides Workflow Connection repository dependency"""
    return SqlAlchemyWorkflowConnectionRepository(db)

def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url)