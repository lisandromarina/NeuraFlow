from typing import List, Optional
from models.schemas.workflow_connection import (
    WorkflowConnection,
    WorkflowConnectionCreate,
    WorkflowConnectionUpdate,
)
from repositories.sqlalchemy_workflow_connection_repository import SqlAlchemyWorkflowConnectionRepository

class WorkflowConnectionService:
    def __init__(self, repository: SqlAlchemyWorkflowConnectionRepository):
        self.repository = repository

    def list_connections(self) -> List[WorkflowConnection]:
        return self.repository.list_all()
    
    def list_connections_by_workflow(self, workflow_id: int) -> List[WorkflowConnection]:
        return self.repository.list_by_workflow_id(workflow_id)

    def get_connection(self, connection_id: int) -> Optional[WorkflowConnection]:
        return self.repository.get_by_id(connection_id)

    def create_connection(self, data: WorkflowConnectionCreate) -> WorkflowConnection:
        return self.repository.add(data)

    def update_connection(self, connection_id: int, data: WorkflowConnectionUpdate) -> Optional[WorkflowConnection]:
        return self.repository.update(connection_id, data)

    def delete_connection(self, connection_id: int) -> bool:
        return self.repository.delete(connection_id)
