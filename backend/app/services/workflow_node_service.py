import json
from core.events import WORKFLOW_UPDATED
from fastapi import HTTPException # type: ignore
from typing import List, Optional
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from models.db_models.workflow_nodes import WorkflowNode
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from repositories.redis_repository import RedisRepository
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from redis import Redis # type: ignore

class WorkflowNodeService:
    def __init__(
            self, 
            workflow_node_repo: SqlAlchemyWorkflowNodeRepository, 
            node_repo: SqlAlchemyNodeRepository,
            workflow_repo: SqlAlchemyWorkflowRepository,
            redis_client: Redis
        ):
        self.workflow_node_repo = workflow_node_repo
        self.node_repo = node_repo 
        self.workflow_repo = workflow_repo
        self.redis_client = redis_client


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
        db_node = self.node_repo.get_node(node_data.node_id)
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

        # Apply updates
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(node, field, value)

        updated_node = self.workflow_node_repo.update(node)
        db_node = self.node_repo.get_node(node.node_id)
        workflow = self.workflow_repo.get_by_id(node.workflow_id)

        # ✅ If workflow is active, notify scheduler
        if workflow and workflow.is_active and db_node.type == "SchedulerNode":
            print("HERE")
            print(updated_node.custom_config)
            event_payload = {
                "workflow_id": workflow.id,
                "nodes": [
                    {
                        "node_id": updated_node.id,
                        "node_type": db_node.type,
                        "custom_config": updated_node.custom_config,
                    }
                ],
            }

            self.redis_client.publish(
                "workflow_events",
                json.dumps({"type": WORKFLOW_UPDATED, "payload": event_payload})
            )

        return updated_node


    # ------------------------
    # Delete
    # ------------------------
    def delete_node(self, node_id: int) -> bool:
        node = self.workflow_node_repo.get_by_id(node_id)
        if not node:
            return False

        db_node = self.node_repo.get_node(node.node_id)
        type = db_node.type  

        # Delete associated trigger schedule
        # self.trigger_service.delete_trigger(type, node)

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

        node_metadata = self.node_repo.get_node(workflow_node.node_id)
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
            "name": node_metadata.name,
            "node_type": node_metadata.type,
            "workflow_id": workflow_node.workflow_id,
            "position_x": workflow_node.position_x,
            "position_y": workflow_node.position_y,
            "inputs": inputs,
            "outputs": outputs
        }