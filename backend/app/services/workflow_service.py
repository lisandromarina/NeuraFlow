from typing import List, Optional
from services.redis_service import RedisService
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from repositories.workflow_repository import WorkflowRepository
from models.schemas.workflow import Workflow
from core.events import WORKFLOW_ACTIVATED, WORKFLOW_DEACTIVATED, WORKFLOW_DELETED
import json

class WorkflowService:
    def __init__(
        self,
        repository: WorkflowRepository,
        wn_repository: SqlAlchemyWorkflowNodeRepository,
        redis_service: RedisService,  # Redis dependency injected
    ):
        self.repository = repository
        self.wn_repository = wn_repository
        self.redis_service = redis_service

    def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        return self.repository.get_by_id(workflow_id)

    def create_workflow(self, name: str, description: str = None) -> Workflow:
        wf = Workflow(name=name, description=description)
        self.repository.add(wf)
        return wf

    def list_workflows(self) -> List[Workflow]:
        return self.repository.list_all()

    def update_workflow_fields(self, workflow_id: int, update_fields: dict) -> Optional[Workflow]:
        wf_db = self.repository.get_by_id(workflow_id)
        if not wf_db:
            return None

        old_is_active = wf_db.is_active
        is_active_changed = False

        for field, value in update_fields.items():
            if hasattr(wf_db, field):
                setattr(wf_db, field, value)
                if field == "is_active" and value != old_is_active:
                    is_active_changed = True

        self.repository.update(wf_db)

        if is_active_changed:
            nodes = self.wn_repository.list_by_workflow_and_type(workflow_id, "SchedulerNode")
            event_payload = {
                "workflow_id": workflow_id,
                "nodes": [
                    {
                        "node_id": n.id,
                        "node_type": n.node_type,
                        "custom_config": n.custom_config,
                    }
                    for n in nodes
                ],
            }
            event_type = WORKFLOW_ACTIVATED if wf_db.is_active else WORKFLOW_DEACTIVATED
            self.redis_service.publish_event(event_type, event_payload)

        return wf_db

    def delete_workflow(self, workflow_id: int) -> bool:
        wf = self.repository.get_by_id(workflow_id)
        if not wf:
            return False

        self.redis_service.publish_event(WORKFLOW_DELETED, {"workflow_id": workflow_id})

        self.repository.delete(workflow_id)
        return True