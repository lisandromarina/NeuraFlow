from typing import List, Optional
from sqlalchemy.orm import Session
from models.db_models.workflow_nodes import WorkflowNode as WorkflowNodeDB
from models.schemas.workflow_node import WorkflowNodeCreate, WorkflowNodeSchema

class SqlAlchemyWorkflowNodeRepository:
    def __init__(self, session: Session):
        self.session = session

    # ------------------------
    # Getters
    # ------------------------
    def get_by_id(self, node_id: int) -> Optional[WorkflowNodeSchema]:
        node_db = self.session.query(WorkflowNodeDB).get(node_id)  # ✅ ORM model
        return WorkflowNodeSchema.from_orm(node_db) if node_db else None

    def list_by_workflow(self, workflow_id: int) -> List[WorkflowNodeSchema]:
        nodes_db = (
            self.session.query(WorkflowNodeDB)  # ✅ ORM model
            .filter(WorkflowNodeDB.workflow_id == workflow_id)
            .all()
        )
        return [WorkflowNodeSchema.from_orm(node) for node in nodes_db]

    # ------------------------
    # Create
    # ------------------------
    def add(self, node_data: WorkflowNodeCreate) -> WorkflowNodeSchema:
        node_db = WorkflowNodeDB(**node_data.dict())
        self.session.add(node_db)
        self.session.commit()
        self.session.refresh(node_db)
        return WorkflowNodeSchema.from_orm(node_db)

    def bulk_add(self, workflow_nodes: List[WorkflowNodeSchema]) -> List[WorkflowNodeSchema]:
        nodes_db = [WorkflowNodeDB(**node.dict()) for node in workflow_nodes]
        self.session.add_all(nodes_db)
        self.session.commit()
        for node_db in nodes_db:
            self.session.refresh(node_db)
        return [WorkflowNodeSchema.from_orm(node_db) for node_db in nodes_db]

    # ------------------------
    # Update
    # ------------------------
    def update(self, workflow_node: WorkflowNodeSchema) -> WorkflowNodeDB:
        node_db = self.session.get(WorkflowNodeDB, workflow_node.id)
        if not node_db:
            return None
        node_db.name = workflow_node.name
        node_db.position_x = workflow_node.position_x
        node_db.position_y = workflow_node.position_y
        node_db.custom_config = workflow_node.custom_config
        self.session.commit()
        self.session.refresh(node_db)  # ensures SQLAlchemy object is up-to-date
        return node_db

    # ------------------------
    # Delete
    # ------------------------
    def delete(self, node_id: int) -> bool:
        node_db = self.session.query(WorkflowNodeDB).get(node_id)
        if not node_db:
            return False
        self.session.delete(node_db)
        self.session.commit()
        return True

    def delete_by_workflow(self, workflow_id: int) -> None:
        self.session.query(WorkflowNodeDB).filter(
            WorkflowNodeDB.workflow_id == workflow_id
        ).delete(synchronize_session=False)
        self.session.commit()
