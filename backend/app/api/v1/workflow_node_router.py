from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from services.workflow_node_service import WorkflowNodeService
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from dependencies import get_workflow_node_repository

router = APIRouter(prefix="/workflow-nodes", tags=["Workflow Nodes"])

@router.get("/{node_id}", response_model=WorkflowNodeSchema)
def get_node(
    node_id: int, 
    repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository)
):
    service = WorkflowNodeService(repo)
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return node

@router.get("/workflow/{workflow_id}", response_model=List[WorkflowNodeSchema])
def list_nodes(
    workflow_id: int, 
    repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository)
):
    service = WorkflowNodeService(repo)
    return service.list_nodes_for_workflow(workflow_id)

@router.post("/", response_model=WorkflowNodeSchema)
def create_node(
    node_data: WorkflowNodeCreate, 
    repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository)
):
    service = WorkflowNodeService(repo)
    return service.create_node(node_data)

@router.put("/{node_id}", response_model=WorkflowNodeSchema)
def update_node(
    node_id: int,
    update_data: WorkflowNodeUpdate,
    repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository)
):
    service = WorkflowNodeService(repo)
    updated_node = service.update_node(node_id, update_data)
    if not updated_node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return updated_node

@router.delete("/{node_id}", response_model=dict)
def delete_node(
    node_id: int,
    repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository)
):
    service = WorkflowNodeService(repo)
    deleted = service.delete_node(node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return {"deleted": True}
