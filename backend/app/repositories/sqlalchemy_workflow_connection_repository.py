from sqlalchemy.orm import Session
from typing import List, Optional
from models.db_models.workflow_connections_db import WorkflowConnection
from models.schemas.workflow_connection import (
    WorkflowConnectionCreate,
    WorkflowConnectionUpdate,
    WorkflowConnection as WorkflowConnectionSchema
)

class SqlAlchemyWorkflowConnectionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, connection_id: int) -> Optional[WorkflowConnectionSchema]:
        conn = self.session.query(WorkflowConnection).get(connection_id)
        return WorkflowConnectionSchema.from_orm(conn) if conn else None

    def list_all(self) -> List[WorkflowConnectionSchema]:
        connections = self.session.query(WorkflowConnection).all()
        return [WorkflowConnectionSchema.from_orm(c) for c in connections]
    
    def list_by_workflow_id(self, workflow_id: int) -> List[WorkflowConnectionSchema]:
        """Return all connections that belong to a specific workflow."""
        connections = (
            self.session.query(WorkflowConnection)
            .filter(WorkflowConnection.workflow_id == workflow_id)
            .all()
        )
        return [WorkflowConnectionSchema.from_orm(c) for c in connections]

    def add(self, connection: WorkflowConnectionCreate) -> WorkflowConnectionSchema:
        conn_db = WorkflowConnection(**connection.dict())
        self.session.add(conn_db)
        self.session.commit()
        self.session.refresh(conn_db)
        return WorkflowConnectionSchema.from_orm(conn_db)

    def update(self, connection_id: int, update_data: WorkflowConnectionUpdate) -> Optional[WorkflowConnectionSchema]:
        conn_db = self.session.query(WorkflowConnection).get(connection_id)
        if not conn_db:
            return None

        # Update only provided fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(conn_db, field, value)

        self.session.commit()
        self.session.refresh(conn_db)
        return WorkflowConnectionSchema.from_orm(conn_db)

    def delete(self, connection_id: int) -> bool:
        conn_db = self.session.query(WorkflowConnection).get(connection_id)
        if conn_db:
            self.session.delete(conn_db)
            self.session.commit()
            return True
        return False
