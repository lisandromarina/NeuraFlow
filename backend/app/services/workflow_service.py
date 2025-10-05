from datetime import datetime, timedelta
from typing import List, Optional
from services.triggers_services import TriggerService
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
        redis_client,  # Redis dependency injected
    ):
        self.repository = repository
        self.wn_repository = wn_repository
        self.redis_client = redis_client

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

        # Update fields dynamically
        for field, value in update_fields.items():
            if hasattr(wf_db, field):
                setattr(wf_db, field, value)
                if field == "is_active" and value != old_is_active:
                    is_active_changed = True

        self.repository.update(wf_db)

        # Handle activation/deactivation via Redis events
        if is_active_changed:
            nodes = self.wn_repository.list_by_workflow_and_type(workflow_id, "SchedulerNode")
            event_payload = {
                "workflow_id": workflow_id,
                "nodes": [{"node_id": n.id, "node_type": n.node_type} for n in nodes]
            }

            if wf_db.is_active:
                self.redis_client.publish(
                    "workflow_events",
                    json.dumps({"type": WORKFLOW_ACTIVATED, "payload": event_payload})
                )
            else:
                self.redis_client.publish(
                    "workflow_events",
                    json.dumps({"type": WORKFLOW_DEACTIVATED, "payload": event_payload})
                )

        return wf_db

    def delete_workflow(self, workflow_id: int) -> bool:
        wf = self.repository.get_by_id(workflow_id)
        if not wf:
            return False

        # Publish deletion event with workflow_id only
        self.redis_client.publish(
            "workflow_events",
            json.dumps({"type": WORKFLOW_DELETED, "payload": {"workflow_id": workflow_id}})
        )

        # Delete the workflow in DB
        self.repository.delete(workflow_id)
        return True