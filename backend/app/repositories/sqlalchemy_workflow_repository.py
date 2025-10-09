from typing import List, Optional
from sqlalchemy.orm import Session # type: ignore
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
        if not wf_db:
            return

        # Use Pydantic's dict to get only set fields
        update_data = workflow.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(wf_db, field):
                setattr(wf_db, field, value)

        self.session.commit()


    def delete(self, workflow_id: int) -> None:
        wf_db = self.session.query(WorkflowDB).get(workflow_id)
        if wf_db:
            self.session.delete(wf_db)
            self.session.commit()

    def get_by_user_id(self, user_id: int):
        return self.session.query(WorkflowDB).filter(WorkflowDB.user_id == user_id).all()