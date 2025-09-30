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
        print("AUX")
        print(aux)
        return aux

    # ------------------------
    # Create
    # ------------------------
    def create_node(self, node_data: WorkflowNodeCreate) -> WorkflowNode:
        # 1. Validate the name
        if not node_data.name or len(node_data.name.strip()) == 0:
            raise ValueError("Node name cannot be empty.")

        # 2. Fetch the Node using NodeService
        db_node = self.node_service.get_node(node_data.node_id)
        if not db_node:
            raise HTTPException(status_code=404, detail="Node not found")

        # 3. Automatically set custom_config using global_config
        node_data.custom_config = db_node.global_config

        # 4. Save WorkflowNode
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
