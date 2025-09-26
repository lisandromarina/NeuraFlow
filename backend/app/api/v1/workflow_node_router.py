from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db_session
from services.workflow_node_service import WorkflowNodeService
from models.schemas.workflow_node import WorkflowNode, WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from typing import List

router = APIRouter(prefix="/workflow-nodes", tags=["Workflow Nodes"])

# Dependency to inject service
def get_workflow_node_service(db: Session = Depends(get_db_session)):
    return WorkflowNodeService(db)

@router.get("/{node_id}", response_model=WorkflowNodeSchema)
def get_node(node_id: int, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")
    return node

@router.get("/workflow/{workflow_id}", response_model=List[WorkflowNodeSchema])
def list_nodes(workflow_id: int, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    return service.list_nodes_for_workflow(workflow_id)

@router.post("/", response_model=WorkflowNode)
def create_node(node_data: WorkflowNodeCreate, service: WorkflowNodeService = Depends(get_workflow_node_service)):
    return service.create_node(node_data)

@router.put("/{node_id}", response_model=WorkflowNodeSchema)
def update_node(node_id: int, update_data: WorkflowNodeUpdate, service: WorkflowNodeService = Depends(get_workflow_node_service)):
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
