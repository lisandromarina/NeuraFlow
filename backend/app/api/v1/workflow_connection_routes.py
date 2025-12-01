from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from dependencies import get_db_session
from models.schemas.workflow_connection import (
    WorkflowConnection,
    WorkflowConnectionCreate,
    WorkflowConnectionUpdate
)
from repositories.sqlalchemy_workflow_connection_repository import SqlAlchemyWorkflowConnectionRepository
from services.workflow_connection_service import WorkflowConnectionService
from auth_dependencies import get_current_user, verify_workflow_ownership, verify_workflow_connection_ownership
from models.db_models.workflow_db import WorkflowDB

router = APIRouter(prefix="/workflow-connections", tags=["Workflow Connections"])

def get_workflow_connection_repository(db: Session = Depends(get_db_session)):
    return SqlAlchemyWorkflowConnectionRepository(db)

@router.get("/", response_model=List[WorkflowConnection])
def list_connections(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    """List all workflow connections (filtered by user's workflows)"""
    service = WorkflowConnectionService(repo)
    connections = service.list_connections()
    # Filter connections by user's workflows
    user_workflow_ids = {w.id for w in db.query(WorkflowDB).filter(WorkflowDB.user_id == current_user["user_id"]).all()}
    return [c for c in connections if c.workflow_id in user_workflow_ids]

@router.post("/", response_model=WorkflowConnection)
def create_connection(
    data: WorkflowConnectionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    """Create a workflow connection (requires ownership of parent workflow)"""
    # Verify ownership of the workflow
    verify_workflow_ownership(data.workflow_id, current_user, db)
    
    service = WorkflowConnectionService(repo)
    return service.create_connection(data)

@router.get("/{connection_id}", response_model=WorkflowConnection)
def get_connection(
    connection_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    """Get a workflow connection (requires ownership of parent workflow)"""
    # Verify ownership
    verify_workflow_connection_ownership(connection_id, current_user, db)
    
    service = WorkflowConnectionService(repo)
    conn = service.get_connection(connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Workflow connection not found")
    return conn

@router.get("/workflow/{workflow_id}", response_model=List[WorkflowConnection])
def list_connections_by_workflow(
    workflow_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    """List connections for a workflow (requires ownership)"""
    # Verify ownership
    verify_workflow_ownership(workflow_id, current_user, db)
    
    service = WorkflowConnectionService(repo)
    return service.list_connections_by_workflow(workflow_id)

@router.put("/{connection_id}", response_model=WorkflowConnection)
def update_connection(
    connection_id: int,
    data: WorkflowConnectionUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    """Update a workflow connection (requires ownership of parent workflow)"""
    # Verify ownership
    verify_workflow_connection_ownership(connection_id, current_user, db)
    
    # If workflow_id is being updated, verify ownership of new workflow
    if hasattr(data, 'workflow_id') and data.workflow_id:
        verify_workflow_ownership(data.workflow_id, current_user, db)
    
    service = WorkflowConnectionService(repo)
    updated = service.update_connection(connection_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Workflow connection not found")
    return updated

@router.delete("/{connection_id}")
def delete_connection(
    connection_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    """Delete a workflow connection (requires ownership of parent workflow)"""
    # Verify ownership
    verify_workflow_connection_ownership(connection_id, current_user, db)
    
    service = WorkflowConnectionService(repo)
    success = service.delete_connection(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow connection not found")
    return {"message": "Workflow connection deleted successfully"}
