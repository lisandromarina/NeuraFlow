from fastapi import APIRouter, Depends, HTTPException
from services.workflow_service import WorkflowService
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from dependencies import get_workflow_repository
from models.schemas.workflow import Workflow, WorkflowUpdate
from typing import List

router = APIRouter(prefix="/workflow", tags=["Workflow"])

@router.get("/", response_model=List[Workflow])
def list_workflows(repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)):
    service = WorkflowService(repo)
    return service.list_workflows()

@router.post("/", response_model=Workflow)
def create_workflow(workflow: Workflow, repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)):
    service = WorkflowService(repo)
    return service.create_workflow(name=workflow.name, description=workflow.description)

@router.get("/{workflow_id}", response_model=Workflow)
def get_workflow(workflow_id: int, repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)):
    service = WorkflowService(repo)
    wf = service.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf

@router.put("/{workflow_id}", response_model=Workflow)
def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)
):
    service = WorkflowService(repo)
    updated = service.update_workflow(
        workflow_id, 
        name=workflow_data.name, 
        description=workflow_data.description
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return updated

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)):
    service = WorkflowService(repo)
    success = service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}
