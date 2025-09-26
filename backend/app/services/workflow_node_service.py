from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeSchema
from models.db_models.workflow_nodes import WorkflowNode


class WorkflowNodeService:
    def __init__(self, session: Session):
        self.repo = SqlAlchemyWorkflowNodeRepository(session)

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
        """
        Create a new workflow node and return the created node with DB-generated id.
        """
        # Example validations
        if not node_data.name or len(node_data.name.strip()) == 0:
            raise ValueError("Node name cannot be empty.")

        if node_data.position_x < 0 or node_data.position_y < 0:
            raise ValueError("Node positions must be positive values.")

        # Add the node and **return the DB result**
        return self.repo.add(node_data)  # <-- return the object with id

    # ------------------------
    # Update
    # ------------------------
    def update_node(self, node_id: int, update_data: WorkflowNodeUpdate) -> Optional[WorkflowNodeSchema]:
        """
        Update a workflow node.
        """
        existing_node = self.repo.get_by_id(node_id)
        if not existing_node:
            return None

        # Merge fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(existing_node, field, value)

        # Commit changes
        self.repo.update(existing_node)
        return self.repo.get_by_id(node_id)

    # ------------------------
    # Delete
    # ------------------------
    def delete_node(self, node_id: int) -> bool:
        """
        Delete a node and return True if it was deleted.
        """
        existing_node = self.repo.get_by_id(node_id)
        if not existing_node:
            return False

        self.repo.delete(node_id)
        return True

    def delete_all_nodes_in_workflow(self, workflow_id: int) -> None:
        """
        Remove all nodes from a given workflow.
        """
        self.repo.delete_by_workflow(workflow_id)
