from typing import List, Optional
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from models.db_models.workflow_nodes import WorkflowNode
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository

class WorkflowNodeService:
    def __init__(self, repo: SqlAlchemyWorkflowNodeRepository):
        self.repo = repo  # already a repository, no Session needed

    # ------------------------
    # Read Operations
    # ------------------------
    def get_node(self, node_id: int) -> Optional[WorkflowNodeSchema]:
        return self.repo.get_by_id(node_id)

    def list_nodes_for_workflow(self, workflow_id: int) -> List[WorkflowNodeSchema]:
        return self.repo.list_by_workflow(workflow_id)

    # ------------------------
    # Create
    # ------------------------
    def create_node(self, node_data: WorkflowNodeCreate) -> WorkflowNode:
        if not node_data.name or len(node_data.name.strip()) == 0:
            raise ValueError("Node name cannot be empty.")
        if node_data.position_x < 0 or node_data.position_y < 0:
            raise ValueError("Node positions must be positive values.")

        return self.repo.add(node_data)

    # ------------------------
    # Update
    # ------------------------
    def update_node(self, node_id: int, update_data: WorkflowNodeUpdate):
        node = self.repo.get_by_id(node_id)

        if not node:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(node, field, value)

        # pass the updated node object
        return self.repo.update(node)

    # ------------------------
    # Delete
    # ------------------------
    def delete_node(self, node_id: int) -> bool:
        return self.repo.delete(node_id)

    def delete_all_nodes_in_workflow(self, workflow_id: int) -> None:
        self.repo.delete_by_workflow(workflow_id)
