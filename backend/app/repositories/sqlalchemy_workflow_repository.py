from typing import List, Optional
from sqlalchemy.orm import Session
from models.db_models.workflow_db import WorkflowDB
from models.schemas.workflow import Workflow
from repositories.workflow_repository import WorkflowRepository

class SqlAlchemyWorkflowRepository(WorkflowRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, workflow_id: int) -> Optional[Workflow]:
        wf = self.session.query(WorkflowDB).get(workflow_id)
        return Workflow.from_orm(wf) if wf else None

    def add(self, workflow: Workflow) -> None:
        wf_db = WorkflowDB(**workflow.dict())
        self.session.add(wf_db)
        self.session.commit()
        workflow.id = wf_db.id

    def list_all(self) -> List[Workflow]:
        workflows = self.session.query(WorkflowDB).all()
        return [Workflow.from_orm(wf) for wf in workflows]

    def update(self, workflow: Workflow) -> None:
        wf_db = self.session.query(WorkflowDB).get(workflow.id)
        if wf_db:
            wf_db.name = workflow.name
            wf_db.description = workflow.description
            self.session.commit()

    def delete(self, workflow_id: int) -> None:
        wf_db = self.session.query(WorkflowDB).get(workflow_id)
        if wf_db:
            self.session.delete(wf_db)
            self.session.commit()
