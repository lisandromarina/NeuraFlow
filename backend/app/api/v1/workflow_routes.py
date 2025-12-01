from fastapi import APIRouter, Depends, HTTPException, Body # type: ignore
from typing import Dict, List

from models.db_models.workflow_db import WorkflowDB
from models.schemas.full_workflow import WorkflowConnectionSchema, WorkflowFullSchema, WorkflowNodeFullSchema
from models.schemas.workflow import Workflow, WorkflowPartialUpdate
from services.redis_service import RedisService
from services.workflow_service import WorkflowService
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from dependencies import (
    get_db_session,
    get_redis_client,
    get_workflow_repository,
    get_workflow_node_repository,
)
from auth_dependencies import get_current_user, verify_workflow_ownership
from core.executor import WorkflowExecutor
from sqlalchemy.orm import Session # type: ignore
from redis import Redis # type: ignore

router = APIRouter(prefix="/workflow", tags=["Workflow"])


# Dependency to provide fully initialized WorkflowService
def get_workflow_service(
    workflow_repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository),
    workflow_node_repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository),
    redis_client: Redis = Depends(get_redis_client)
) -> WorkflowService:
    redis_service = RedisService(redis_client)
    return WorkflowService(workflow_repo, workflow_node_repo, redis_service)

@router.get("/", response_model=List[Workflow])
def list_workflows(
    current_user: dict = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """List all workflows for the current user"""
    # Filter workflows by current user
    workflows = service.get_workflows_by_user(current_user["user_id"])
    return workflows


@router.post("/", response_model=Workflow)
def create_workflow(
    workflow: Workflow,
    current_user: dict = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create a new workflow for the current user"""
    # Ensure user_id matches current user
    workflow.user_id = current_user["user_id"]
    return service.create_workflow(
        name=workflow.name,
        description=workflow.description,
        user_id=workflow.user_id 
    )

@router.get("/{workflow_id}", response_model=Workflow)
def get_workflow(
    workflow_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get a specific workflow (requires ownership)"""
    # Verify ownership
    verify_workflow_ownership(workflow_id, current_user, db)
    
    wf = service.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.put("/{workflow_id}", response_model=Workflow)
def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowPartialUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Update a workflow (requires ownership)"""
    # Verify ownership
    verify_workflow_ownership(workflow_id, current_user, db)
    
    update_fields = {k: v for k, v in workflow_data.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    updated_workflow = service.update_workflow_fields(workflow_id, update_fields)
    if not updated_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return updated_workflow


@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Delete a workflow (requires ownership)"""
    # Verify ownership
    verify_workflow_ownership(workflow_id, current_user, db)
    
    success = service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}


@router.get("/{workflow_id}/full", response_model=WorkflowFullSchema)
def get_full_workflow(
    workflow_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get full workflow with nodes and connections (requires ownership)"""
    # Verify ownership
    verify_workflow_ownership(workflow_id, current_user, db)
    
    workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    nodes = [
        WorkflowNodeFullSchema.from_orm({
            **w_node.__dict__,
            "node_type": w_node.node.type if w_node.node else None,
            "node_category": w_node.node.category if w_node.node else None
        })
        for w_node in workflow.nodes
    ]

    connections = [WorkflowConnectionSchema.from_orm(c) for c in workflow.connections]

    return WorkflowFullSchema(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        is_active=workflow.is_active,
        nodes=nodes,
        connections=connections
    )


@router.post("/{workflow_id}/execute")
def execute_workflow(
    workflow_id: int,
    context: Dict = Body(default={}),
    current_user: dict = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
    db: Session = Depends(get_db_session)
):
    """Execute a workflow (requires ownership)"""
    # Verify ownership
    verify_workflow_ownership(workflow_id, current_user, db)
    
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    executor = WorkflowExecutor(db)
    try:
        executor.execute_workflow(workflow_id, context=context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

    return {"message": f"Workflow {workflow_id} executed successfully"}


@router.get("/user/{user_id}", response_model=List[Workflow])
def get_workflows_by_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Get all workflows belonging to a specific user.
    Users can only access their own workflows.
    """
    # Ensure user can only access their own workflows
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own workflows")
    
    workflows = service.get_workflows_by_user(user_id)
    if not workflows:
        raise HTTPException(status_code=404, detail="No workflows found for this user")
    return workflows