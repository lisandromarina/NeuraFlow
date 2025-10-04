from services.triggers_services import TriggerService
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from models.db_models.workflow_db import Base

DATABASE_URL="postgresql://postgres:postgres@postgres:5432/mydatabase"

# 1. Create engine and session
engine = create_engine(DATABASE_URL, echo=True)
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

def get_trigger_service() -> TriggerService:
    """Provides a new instance of TriggerService"""
    return TriggerService()
