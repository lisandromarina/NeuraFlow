from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from fastapi import APIRouter, Depends, HTTPException # type: ignore
from typing import List
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from services.redis_service import RedisService
from services.workflow_node_service import WorkflowNodeService
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from repositories.sqlalchemy_workflow_connection_repository import SqlAlchemyWorkflowConnectionRepository
from dependencies import get_redis_client, get_user_credential_repository, get_workflow_repository, get_workflow_node_repository, get_node_repository, get_workflow_connection_repository, get_db_session
from auth_dependencies import get_current_user, verify_workflow_ownership, verify_workflow_node_ownership
from sqlalchemy.orm import Session # type: ignore
from redis import Redis # type: ignore

router = APIRouter(prefix="/workflow-nodes", tags=["Workflow Nodes"])


def get_workflow_node_service(
    workflow_node_repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository),
    node_repo: SqlAlchemyNodeRepository = Depends(get_node_repository),
    workflow_repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository),
    credentials_repo: SqlAlchemyUserCredentialRepository = Depends(get_user_credential_repository),
    redis_client: Redis = Depends(get_redis_client),
    workflow_connection_repo: SqlAlchemyWorkflowConnectionRepository = Depends(get_workflow_connection_repository)
    # trigger_service: TriggerService = Depends(get_trigger_service),
) -> WorkflowNodeService:
    """Factory function to provide a fully constructed WorkflowNodeService"""
    redis_service = RedisService(redis_client)
    return WorkflowNodeService(workflow_node_repo, node_repo, workflow_repo, credentials_repo, redis_service, workflow_connection_repo)


@router.get("/{node_id}", response_model=WorkflowNodeSchema)
def get_node(
    node_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowNodeService = Depends(get_workflow_node_service)
):
    """Get a workflow node (requires ownership of parent workflow)"""
    # Verify ownership
    verify_workflow_node_ownership(node_id, current_user, db)
    
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return node


@router.get("/workflow/{workflow_id}", response_model=List[WorkflowNodeSchema])
def list_nodes(
    workflow_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowNodeService = Depends(get_workflow_node_service)
):
    """List all nodes for a workflow (requires ownership)"""
    # Verify ownership
    verify_workflow_ownership(workflow_id, current_user, db)
    
    return service.list_nodes_for_workflow(workflow_id)


@router.post("/", response_model=WorkflowNodeSchema)
def create_node(
    node_data: WorkflowNodeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowNodeService = Depends(get_workflow_node_service)
):
    """Create a workflow node (requires ownership of parent workflow)"""
    # Verify ownership of the workflow
    verify_workflow_ownership(node_data.workflow_id, current_user, db)
    
    return service.create_node(node_data)


@router.put("/{node_id}", response_model=WorkflowNodeSchema)
def update_node(
    node_id: int,
    update_data: WorkflowNodeUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowNodeService = Depends(get_workflow_node_service)
):
    """Update a workflow node (requires ownership of parent workflow)"""
    # Verify ownership
    verify_workflow_node_ownership(node_id, current_user, db)
    
    # If workflow_id is being updated, verify ownership of new workflow
    if hasattr(update_data, 'workflow_id') and update_data.workflow_id:
        verify_workflow_ownership(update_data.workflow_id, current_user, db)
    
    updated_node = service.update_node(node_id, update_data)
    if not updated_node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return updated_node


@router.delete("/{node_id}", response_model=dict)
def delete_node(
    node_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowNodeService = Depends(get_workflow_node_service)
):
    """Delete a workflow node (requires ownership of parent workflow)"""
    # Verify ownership
    verify_workflow_node_ownership(node_id, current_user, db)
    
    deleted = service.delete_node(node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return {"deleted": True}


@router.get("/ui-schema/{workflow_node_id}", response_model=dict)
def get_node_ui_schema(
    workflow_node_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowNodeService = Depends(get_workflow_node_service)
):
    """Get UI schema for a workflow node (requires ownership of parent workflow)"""
    # Verify ownership
    verify_workflow_node_ownership(workflow_node_id, current_user, db)
    
    return service.get_node_ui_schema(workflow_node_id)