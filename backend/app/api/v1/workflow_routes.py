from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, List

from models.db_models.workflow_db import WorkflowDB
from models.schemas.full_workflow import WorkflowConnectionSchema, WorkflowFullSchema, WorkflowNodeFullSchema
from models.schemas.workflow import Workflow, WorkflowPartialUpdate
from services.workflow_service import WorkflowService
from services.triggers_services import TriggerService
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from dependencies import (
    get_db_session,
    get_redis_client,
    get_workflow_repository,
    get_workflow_node_repository,
    get_trigger_service
)
from sqlalchemy.orm import Session # type: ignore
from redis import Redis # type: ignore

router = APIRouter(prefix="/workflow", tags=["Workflow"])


# Dependency to provide fully initialized WorkflowService
def get_workflow_service(
    workflow_repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository),
    workflow_node_repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository),
    redis_client: Redis = Depends(get_redis_client)
) -> WorkflowService:
    return WorkflowService(workflow_repo, workflow_node_repo, redis_client)


@router.get("/", response_model=List[Workflow])
def list_workflows(service: WorkflowService = Depends(get_workflow_service)):
    return service.list_workflows()


@router.post("/", response_model=Workflow)
def create_workflow(
    workflow: Workflow, 
    service: WorkflowService = Depends(get_workflow_service)
):
    return service.create_workflow(name=workflow.name, description=workflow.description)


@router.get("/{workflow_id}", response_model=Workflow)
def get_workflow(
    workflow_id: int, 
    service: WorkflowService = Depends(get_workflow_service)
):
    wf = service.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.put("/{workflow_id}", response_model=Workflow)
def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowPartialUpdate,
    service: WorkflowService = Depends(get_workflow_service)
):
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
    service: WorkflowService = Depends(get_workflow_service)
):
    success = service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}


@router.get("/{workflow_id}/full", response_model=WorkflowFullSchema)
def get_full_workflow(
    workflow_id: int,
    db: Session = Depends(get_db_session)
):
    workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    nodes = [
        WorkflowNodeFullSchema.from_orm({
            **w_node.__dict__,
            "node_type": w_node.node.type if w_node.node else None
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
    service: WorkflowService = Depends(get_workflow_service),
    db: Session = Depends(get_db_session)
):
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    from core.executor import WorkflowExecutor
    executor = WorkflowExecutor(db)
    try:
        executor.execute_workflow(workflow_id, context=context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

    return {"message": f"Workflow {workflow_id} executed successfully"}
