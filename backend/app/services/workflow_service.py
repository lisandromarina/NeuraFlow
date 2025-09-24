from typing import List, Optional
from repositories.workflow_repository import WorkflowRepository
from models.schemas.workflow import Workflow

class WorkflowService:
    def __init__(self, repository: WorkflowRepository):
        self.repository = repository

    def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        return self.repository.get_by_id(workflow_id)

    def create_workflow(self, name: str, description: str = None) -> Workflow:
        wf = Workflow(name=name, description=description)
        self.repository.add(wf)
        return wf

    def list_workflows(self) -> List[Workflow]:
        return self.repository.list_all()

    def update_workflow(self, workflow_id: int, name: str, description: str = None) -> Optional[Workflow]:
        wf = self.repository.get_by_id(workflow_id)
        if wf:
            wf.name = name
            wf.description = description
            self.repository.update(wf)
            return wf
        return None

    def delete_workflow(self, workflow_id: int) -> bool:
        wf = self.repository.get_by_id(workflow_id)
        if wf:
            self.repository.delete(workflow_id)
            return True
        return False
