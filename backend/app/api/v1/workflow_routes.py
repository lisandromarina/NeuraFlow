from models.db_models.workflow_db import WorkflowDB
from models.schemas.full_workflow import WorkflowConnectionSchema, WorkflowFullSchema, WorkflowNodeFullSchema
from dependencies import get_db_session
from core.executor import WorkflowExecutor
from fastapi import APIRouter, Depends, HTTPException, Body
from services.workflow_service import WorkflowService
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from dependencies import get_workflow_repository
from models.schemas.workflow import Workflow, WorkflowPartialUpdate, WorkflowUpdate
from typing import Dict, List
from sqlalchemy.orm import Session

router = APIRouter(prefix="/workflow", tags=["Workflow"])

@router.get("/", response_model=List[Workflow])
def list_workflows(repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)):
    service = WorkflowService(repo)
    return service.list_workflows()

@router.post("/", response_model=Workflow)
def create_workflow(
    workflow: Workflow, 
    repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)
):
    service = WorkflowService(repo)
    return service.create_workflow(name=workflow.name, description=workflow.description)

@router.get("/{workflow_id}", response_model=Workflow)
def get_workflow(
    workflow_id: int, 
    repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)
):
    service = WorkflowService(repo)
    wf = service.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf

@router.put("/{workflow_id}", response_model=Workflow)
def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowPartialUpdate,
    repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)
):
    service = WorkflowService(repo)

    print("Parsed model:", workflow_data.dict())

    # ✅ Collect only non-null fields
    update_fields = {
        key: value
        for key, value in workflow_data.dict().items()
        if value is not None
    }
    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    updated_workflow = service.update_workflow_fields(workflow_id, update_fields)

    if not updated_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return updated_workflow

@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int, 
    repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository)
):
    service = WorkflowService(repo)
    success = service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}

@router.get("/{workflow_id}/full", response_model=WorkflowFullSchema)
def get_full_workflow(
    workflow_id: int,
    db: Session = Depends(get_db_session)
):
    # Fetch workflow
    workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Fetch nodes and include node_type
    nodes = []
    for w_node in workflow.nodes:
        nodes.append(
            WorkflowNodeFullSchema.from_orm({
                **w_node.__dict__,
                "node_type": w_node.node.type if w_node.node else None
            })
        )

    # Fetch connections
    connections = [WorkflowConnectionSchema.from_orm(c) for c in workflow.connections]

    return WorkflowFullSchema(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        is_active=workflow.is_active,
        nodes=nodes,
        connections=connections
    )


# --- New route to trigger workflow execution ---
@router.post("/{workflow_id}/execute")
def execute_workflow(
    workflow_id: int,
    context: Dict = Body(default={}),  # Optional runtime variables
    repo: SqlAlchemyWorkflowRepository = Depends(get_workflow_repository),
    db: Session = Depends(get_db_session)
):
    service = WorkflowService(repo)
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    executor = WorkflowExecutor(db)
    try:
        executor.execute_workflow(workflow_id, context=context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

    return {"message": f"Workflow {workflow_id} executed successfully"}
    