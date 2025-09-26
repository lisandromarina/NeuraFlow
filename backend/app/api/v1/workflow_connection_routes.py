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

router = APIRouter(prefix="/workflow-connections", tags=["Workflow Connections"])

def get_workflow_connection_repository(db: Session = Depends(get_db_session)):
    return SqlAlchemyWorkflowConnectionRepository(db)

@router.get("/", response_model=List[WorkflowConnection])
def list_connections(repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)):
    service = WorkflowConnectionService(repo)
    return service.list_connections()

@router.post("/", response_model=WorkflowConnection)
def create_connection(
    data: WorkflowConnectionCreate,
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    service = WorkflowConnectionService(repo)
    return service.create_connection(data)

@router.get("/{connection_id}", response_model=WorkflowConnection)
def get_connection(
    connection_id: int,
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    service = WorkflowConnectionService(repo)
    conn = service.get_connection(connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Workflow connection not found")
    return conn

@router.get("/workflow/{workflow_id}", response_model=List[WorkflowConnection])
def list_connections_by_workflow(
    workflow_id: int,
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    service = WorkflowConnectionService(repo)
    return service.list_connections_by_workflow(workflow_id)

@router.put("/{connection_id}", response_model=WorkflowConnection)
def update_connection(
    connection_id: int,
    data: WorkflowConnectionUpdate,
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    service = WorkflowConnectionService(repo)
    updated = service.update_connection(connection_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Workflow connection not found")
    return updated

@router.delete("/{connection_id}")
def delete_connection(
    connection_id: int,
    repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
):
    service = WorkflowConnectionService(repo)
    success = service.delete_connection(connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow connection not found")
    return {"message": "Workflow connection deleted successfully"}
