from fastapi import HTTPException
from typing import List, Optional
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from models.db_models.workflow_nodes import WorkflowNode
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from services.node_service import NodeService  # <-- Import your NodeService

class WorkflowNodeService:
    def __init__(self, workflow_node_repo: SqlAlchemyWorkflowNodeRepository, node_service: NodeService):
        self.workflow_node_repo = workflow_node_repo
        self.node_service = node_service  # Use NodeService instead of direct DB calls

    # ------------------------
    # Read Operations
    # ------------------------
    def get_node(self, node_id: int) -> Optional[WorkflowNodeSchema]:
        return self.workflow_node_repo.get_by_id(node_id)

    def list_nodes_for_workflow(self, workflow_id: int) -> List[WorkflowNodeSchema]:
        aux = self.workflow_node_repo.list_by_workflow(workflow_id)
        return aux

    # ------------------------
    # Create
    # ------------------------
    def create_node(self, node_data: WorkflowNodeCreate) -> WorkflowNode:
        # 1. Validate the name
        if not node_data.name or len(node_data.name.strip()) == 0:
            raise ValueError("Node name cannot be empty.")

        # 2. Fetch the Node definition
        db_node = self.node_service.get_node(node_data.node_id)
        if not db_node:
            raise HTTPException(status_code=404, detail="Node not found")

        # 3. Build default custom_config from config_metadata
        config_metadata = db_node.config_metadata or {}
        custom_config = {}

        for input_def in config_metadata.get("inputs", []):
            field_name = input_def["name"]
            default_value = input_def.get("default")
            custom_config[field_name] = default_value if default_value is not None else None

        # 4. Set the custom_config
        node_data.custom_config = custom_config

        # 5. Save WorkflowNode
        return self.workflow_node_repo.add(node_data)

    # ------------------------
    # Update
    # ------------------------
    def update_node(self, node_id: int, update_data: WorkflowNodeUpdate):
        node = self.workflow_node_repo.get_by_id(node_id)

        if not node:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(node, field, value)

        return self.workflow_node_repo.update(node)

    # ------------------------
    # Delete
    # ------------------------
    def delete_node(self, node_id: int) -> bool:
        return self.workflow_node_repo.delete(node_id)

    def delete_all_nodes_in_workflow(self, workflow_id: int) -> None:
        self.workflow_node_repo.delete_by_workflow(workflow_id)


    # ------------------------
    # UI Schema Merge
    # ------------------------
    def get_node_ui_schema(self, workflow_node_id: int) -> dict:
        """
        Return a WorkflowNode merged with its Node metadata,
        ready for UI display (labels, defaults, and current custom_config values).
        """
        workflow_node = self.workflow_node_repo.get_by_id(workflow_node_id)
        if not workflow_node:
            raise HTTPException(status_code=404, detail="WorkflowNode not found")

        node_metadata = self.node_service.get_node(workflow_node.node_id)
        if not node_metadata:
            raise HTTPException(status_code=404, detail="Node definition not found")

        config_metadata = node_metadata.config_metadata or {}
        custom_config = workflow_node.custom_config or {}

        # Merge inputs with values
        inputs = []
        for input_def in config_metadata.get("inputs", []):
            name = input_def["name"]
            value = custom_config.get(name, input_def.get("default"))
            inputs.append({**input_def, "value": value})

        outputs = config_metadata.get("outputs", [])

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