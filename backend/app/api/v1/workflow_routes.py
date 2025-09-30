from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from models.db_models.workflow_db import WorkflowDB
from models.schemas.full_workflow import WorkflowConnectionSchema, WorkflowFullSchema, WorkflowNodeFullSchema
from dependencies import get_db_session, get_node_repository, get_workflow_node_repository
from core.executor import WorkflowExecutor
from fastapi import APIRouter, Depends, HTTPException, Body
from services.workflow_service import WorkflowService
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from dependencies import get_workflow_repository
from models.schemas.workflow import Workflow, WorkflowUpdate
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


@router.get("/ui-schema/{workflow_node_id}", response_model=dict)
def get_node_ui_schema(
    workflow_node_id: int,
    workflow_node_repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository),
    node_repo: SqlAlchemyNodeRepository = Depends(get_node_repository)
):
    """
    Return a WorkflowNode merged with its Node metadata,
    ready for UI display (labels, defaults, and current custom_config values).
    """
    # 1. Get the workflow node
    workflow_node = workflow_node_repo.get_by_id(workflow_node_id)
    if not workflow_node:
        raise HTTPException(status_code=404, detail="WorkflowNode not found")

    # 2. Get the node definition
    node_metadata = node_repo.get_by_id(workflow_node.node_id)
    if not node_metadata:
        raise HTTPException(status_code=404, detail="Node definition not found")

    # 3. Merge custom_config with config_metadata
    def build_node_ui_schema(node_metadata: dict, custom_config: dict) -> dict:
        inputs = []
        for field in node_metadata.get("config_metadata", {}).get("inputs", []):
            name = field["name"]
            value = custom_config.get(name, field.get("default"))
            inputs.append({**field, "value": value})

        outputs = node_metadata.get("config_metadata", {}).get("outputs", [])

        return {
            "id": workflow_node.id,
            "name": workflow_node.name,
            "node_type": node_metadata.type,
            "workflow_id": workflow_node.workflow_id,
            "position_x": workflow_node.position_x,
            "position_y": workflow_node.position_y,
            "inputs": inputs,
            "outputs": outputs
        }

    ui_schema = build_node_ui_schema(node_metadata.__dict__, workflow_node.custom_config or {})
    return ui_schema