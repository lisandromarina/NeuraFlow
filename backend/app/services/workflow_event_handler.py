from services.scheduler_service import SchedulerService
from services.node_processor_service import NodeProcessorService
from core.events import WORKFLOW_UPDATED, WORKFLOW_DELETED, WORKFLOW_DEACTIVATED, WORKFLOW_ACTIVATED

# Only categories we support for processing nodes
SUPPORTED_CATEGORIES = {"SchedulerService"}  # extend this set as needed

class WorkflowEventHandler:
    def __init__(
            self, 
            node_processor_service: NodeProcessorService, 
            scheduler_service: SchedulerService
        ):
        self.node_processor_service: NodeProcessorService = node_processor_service
        self.scheduler_service = scheduler_service

    def handle_event(self, event_type: str, payload: dict):
        workflow_id = payload.get("workflow_id")
        nodes = payload.get("nodes", [])

        if not workflow_id:
            print("[WorkflowEventHandler] Missing workflow_id in event payload", flush=True)
            return

        if event_type in [WORKFLOW_ACTIVATED, WORKFLOW_UPDATED]:
            for node in nodes:
                if node.get("node_type") != "trigger":
                    continue
                self.node_processor_service.process(node, workflow_id)

        elif event_type in [WORKFLOW_DEACTIVATED, WORKFLOW_DELETED]:
            for node in nodes:
                self.node_processor_service.remove(node, workflow_id)