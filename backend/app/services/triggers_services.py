from datetime import datetime, timedelta
import json
from services.scheduler_service import SchedulerService  # adjust import path

class TriggerService:
    def __init__(self):
        self.scheduler_service = SchedulerService()

    def handle_node_update(self, type, updated_node):
        """
        Called whenever a workflow node is updated.
        Determines if the node is a trigger node (e.g. SchedulerNode) and updates its trigger config.
        """
        config = getattr(updated_node, "custom_config", {}) or {}
        workflow_id = getattr(updated_node, "workflow_id", None)

        if type == "SchedulerNode":
            self._update_scheduler_trigger(workflow_id, config)

        # In the future, you can handle other types:
        # elif node_type == "WebhookNode":
        #     self._update_webhook_trigger(workflow_id, config)

    def _update_scheduler_trigger(self, workflow_id, config):
        """Register or update a scheduler trigger in Redis."""
        if isinstance(config, str):
            try:
                config = config.replace("'", '"')  # convert single quotes to double quotes
                config = json.loads(config)
            except json.JSONDecodeError:
                print(f"[TriggerService] Failed to parse config string: {config}")
                config = {}


        delay_seconds = config.get("delay_seconds", 0)
        interval_seconds = config.get("interval_seconds", None)
        until = config.get("until", None)
        max_occurrences = config.get("max_occurrences", None)
        context = {}

        start_time = datetime.utcnow() + timedelta(seconds=delay_seconds)

        self.scheduler_service.register_schedule(
            workflow_id=workflow_id,
            start_time=start_time,
            interval_seconds=interval_seconds,
            max_occurrences=max_occurrences,
            until=until,
            context=context,
        )

        print(f"[TriggerService] Updated scheduler for workflow {workflow_id}")

    def delete_trigger(self, type, node):
        """Remove a trigger when a node is deleted."""
        workflow_id = getattr(node, "workflow_id", None)

        if type == "SchedulerNode":
            self.scheduler_service.r.hdel("workflow_schedules", workflow_id)
            print(f"[TriggerService] Removed scheduler for workflow {workflow_id}")
