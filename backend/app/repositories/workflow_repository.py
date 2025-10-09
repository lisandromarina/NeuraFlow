from abc import ABC, abstractmethod
from typing import List, Optional
from models.schemas.workflow import Workflow

class WorkflowRepository(ABC):
    @abstractmethod
    def get_by_id(self, workflow_id: int) -> Optional[Workflow]:
        pass

    @abstractmethod
    def add(self, workflow: Workflow) -> None:
        pass

    @abstractmethod
    def list_all(self) -> List[Workflow]:
        pass

    @abstractmethod
    def update(self, workflow: Workflow) -> None:
        pass

    @abstractmethod
    def delete(self, workflow_id: int) -> None:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> None:
        pass
