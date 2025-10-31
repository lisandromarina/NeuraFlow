import json
from core.events import WORKFLOW_DELETED, WORKFLOW_UPDATED
from fastapi import HTTPException # type: ignore
from typing import List, Optional
from models.schemas.workflow import Workflow
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from models.db_models.workflow_nodes import WorkflowNode
from services.redis_service import RedisService
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from repositories.sqlalchemy_workflow_connection_repository import SqlAlchemyWorkflowConnectionRepository
from redis import Redis # type: ignore
from models.db_models.node_db import Node
from utils.token_security import decrypt_credentials

class WorkflowNodeService:
    def __init__(
            self, 
            workflow_node_repo: SqlAlchemyWorkflowNodeRepository, 
            node_repo: SqlAlchemyNodeRepository,
            workflow_repo: SqlAlchemyWorkflowRepository,
            credentials_repo: SqlAlchemyUserCredentialRepository,
            redis_service: RedisService,
            workflow_connection_repo: SqlAlchemyWorkflowConnectionRepository,
        ):
        self.workflow_node_repo = workflow_node_repo
        self.node_repo = node_repo 
        self.workflow_repo = workflow_repo
        self.credentials_repo = credentials_repo
        self.redis_service = redis_service
        self.workflow_connection_repo = workflow_connection_repo


    # ------------------------
    # Read Operations
    # ------------------------
    def get_node(self, node_id: int) -> Optional[WorkflowNodeSchema]:
        return self.workflow_node_repo.get_by_id(node_id)

    def list_nodes_for_workflow(self, workflow_id: int) -> List[WorkflowNodeSchema]:
        aux = self.workflow_node_repo.list_by_workflow(workflow_id)
        return aux

    def get_parent_outputs(self, workflow_node_id: int) -> List[dict]:
        """
        Get parent nodes and their outputs for a given workflow node.
        Returns a list of parent nodes with their output metadata.
        """
        # Get all connections for this workflow
        workflow_node = self.workflow_node_repo.get_by_id(workflow_node_id)
        if not workflow_node:
            return []
        
        connections = self.workflow_connection_repo.list_by_workflow_id(workflow_node.workflow_id)
        
        # Find parent nodes (nodes that connect TO this node)
        parent_node_ids = []
        for connection in connections:
            if connection.to_step_id == workflow_node_id:
                parent_node_ids.append(connection.from_step_id)
        
        # Get parent nodes and their output metadata
        parent_outputs = []
        for parent_id in parent_node_ids:
            parent_workflow_node = self.workflow_node_repo.get_by_id(parent_id)
            if parent_workflow_node:
                parent_node = self.node_repo.get_node(parent_workflow_node.node_id)
                if parent_node:
                    config_metadata = parent_node.config_metadata or {}
                    outputs = config_metadata.get("outputs", [])
                    parent_outputs.append({
                        "parent_id": parent_id,
                        "parent_name": parent_workflow_node.name,
                        "parent_node_type": parent_node.type,
                        "outputs": outputs
                    })
        
        return parent_outputs

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

        workflow = self.workflow_repo.get_by_id(node.workflow_id)

        # Apply updates
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(node, field, value)

        if workflow:
            if node.custom_config is None:
                node.custom_config = {}
            else:
                node.custom_config = dict(node.custom_config)  # ensure it's mutable
            node.custom_config["user_id"] = workflow.user_id

        updated_node = self.workflow_node_repo.update(node)
        db_node = self.node_repo.get_node(node.node_id)

        # ✅ If workflow is active, notify scheduler
        if workflow and workflow.is_active and db_node.type == "trigger":
            event_payload = {
                "workflow_id": workflow.id,
                "nodes": [
                    {
                        "node_id": updated_node.id,
                        "node_type": db_node.type,
                        "node_category": db_node.category,
                        "custom_config": updated_node.custom_config,
                    }
                ],
            }

            self.redis_service.publish_event(WORKFLOW_UPDATED, event_payload)

        return updated_node


    # ------------------------
    # Delete
    # ------------------------
    def delete_node(self, node_id: int) -> bool:
        node = self.workflow_node_repo.get_by_id(node_id)
        if not node:
            return False

        deleted = self.workflow_node_repo.delete(node_id)

        if deleted:
            # Notify Redis that a workflow node was deleted
            self.redis_service.publish_event(WORKFLOW_DELETED, {"workflow_id": node.workflow_id})

        return deleted

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
        workflow_node: WorkflowNodeSchema = self.workflow_node_repo.get_by_id(workflow_node_id)
        if not workflow_node:
            raise HTTPException(status_code=404, detail="WorkflowNode not found")

        node: Node = self.node_repo.get_node(workflow_node.node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node definition not found")

        config_metadata = node.config_metadata or {}
        custom_config = workflow_node.custom_config or {}

        # Merge inputs with values
        inputs = []
        for input_def in config_metadata.get("inputs", []):
            name = input_def["name"]
            value = custom_config.get(name, input_def.get("default"))
            inputs.append({**input_def, "value": value})

        outputs = config_metadata.get("outputs", [])
        credentials = config_metadata.get("credentials")
        hasCred = False
        if(credentials):
            metadata_scope = credentials.get("scopes", [])
            credentials_name = credentials.get("name")

            workflow: Workflow = self.workflow_repo.get_by_id(workflow_node.workflow_id)

            auth = self.credentials_repo.get_by_user_and_service(workflow.user_id, credentials_name)
            
            if(auth):
                cred = decrypt_credentials(auth.credentials)
                scope = cred.get("scope")
                scope_list = set(scope.split())
                metadata_set = set(metadata_scope)
                if metadata_set.issubset(scope_list):
                    hasCred = True

        # Get parent outputs
        parents_outputs = self.get_parent_outputs(workflow_node_id)

        return {
            "id": workflow_node.id,
            "name": node.name,
            "node_type": node.type,
            "workflow_id": workflow_node.workflow_id,
            "position_x": workflow_node.position_x,
            "position_y": workflow_node.position_y,
            "inputs": inputs,
            "outputs": outputs,
            "credentials": credentials,
            "hasCredentials": hasCred,
            "linkable_fields": config_metadata.get("linkable_fields", []),
            "parents_outputs": parents_outputs
        }