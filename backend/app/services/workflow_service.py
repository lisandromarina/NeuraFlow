from datetime import datetime, timedelta
from typing import List, Optional
from services.triggers_services import TriggerService
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from repositories.workflow_repository import WorkflowRepository
from models.schemas.workflow import Workflow

class WorkflowService:
    def __init__(
            self, 
            repository: WorkflowRepository, 
            wn_repository: SqlAlchemyWorkflowNodeRepository,
            trigger_service : TriggerService
        ):
        self.repository = repository
        self.wn_repository = wn_repository
        self.trigger_service = trigger_service

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

        # Handle activation/deactivation
        if is_active_changed:
            if wf_db.is_active:
                # ✅ Workflow reactivated → register schedules
                scheduler_nodes = self.wn_repository.list_by_workflow_and_type(workflow_id, "SchedulerNode")

                for wf_node in scheduler_nodes:
                    self.trigger_service.handle_node_update(
                        wf_node.node_type,
                        wf_node
                    )

            else:
                # ❌ Workflow deactivated → delete triggers
                scheduler_nodes = self.wn_repository.list_by_workflow_and_type(workflow_id, "SchedulerNode")

                for wf_node in scheduler_nodes:
                    self.trigger_service.delete_trigger(
                        wf_node.node_type,
                        wf_node
                    )

        return wf_db
    
    def delete_workflow(self, workflow_id: int) -> bool:
        wf = self.repository.get_by_id(workflow_id)
        if not wf:
            return False

        # ✅ Get all nodes belonging to this workflow
        workflow_nodes = self.wn_repository.list_by_workflow_and_type(workflow_id, "SchedulerNode")

        # ✅ Loop through each node and delete its trigger if needed
        for node in workflow_nodes:
            # You can access type via relationship (node.node.type) or node.node_type if you stored it in schema
            type = node.node_type
            if type in ("SchedulerNode", "TriggerNode"):
                # Call your TriggerService delete logic
                self.trigger_service.delete_trigger(type, node)

        # ✅ Finally delete the workflow itself
        self.repository.delete(workflow_id)
        return True