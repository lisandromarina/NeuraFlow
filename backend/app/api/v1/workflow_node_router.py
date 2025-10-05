from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from services.triggers_services import TriggerService
from fastapi import APIRouter, Depends, HTTPException # type: ignore
from typing import List
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from services.workflow_node_service import WorkflowNodeService
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from dependencies import get_workflow_repository, get_workflow_node_repository, get_node_repository, get_trigger_service

router = APIRouter(prefix="/workflow-nodes", tags=["Workflow Nodes"])


def get_workflow_node_service(
    workflow_node_repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository),
    node_repo: SqlAlchemyNodeRepository = Depends(get_node_repository),
    workflow_repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository),
    # trigger_service: TriggerService = Depends(get_trigger_service),
) -> WorkflowNodeService:
    """Factory function to provide a fully constructed WorkflowNodeService"""
    return WorkflowNodeService(workflow_node_repo, node_repo, workflow_repo)


@router.get("/{node_id}", response_model=WorkflowNodeSchema)
def get_node(node_id: int, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return node


@router.get("/workflow/{workflow_id}", response_model=List[WorkflowNodeSchema])
def list_nodes(workflow_id: int, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    return service.list_nodes_for_workflow(workflow_id)


@router.post("/", response_model=WorkflowNodeSchema)
def create_node(node_data: WorkflowNodeCreate, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    return service.create_node(node_data)


@router.put("/{node_id}", response_model=WorkflowNodeSchema)
def update_node(
    node_id: int,
    update_data: WorkflowNodeUpdate,
    service: WorkflowNodeService = Depends(get_workflow_node_service)
):
    updated_node = service.update_node(node_id, update_data)
    if not updated_node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return updated_node


@router.delete("/{node_id}", response_model=dict)
def delete_node(node_id: int, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    deleted = service.delete_node(node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return {"deleted": True}


@router.get("/ui-schema/{workflow_node_id}", response_model=dict)
def get_node_ui_schema(workflow_node_id: int, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    return service.get_node_ui_schema(workflow_node_id)