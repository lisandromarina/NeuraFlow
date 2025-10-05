import json
import datetime
from models.schemas.schedule import Schedule
from core.events import WORKFLOW_UPDATED, WORKFLOW_DELETED, WORKFLOW_DEACTIVATED, WORKFLOW_ACTIVATED

class WorkflowEventHandler:
    def __init__(self, scheduler_service):
        self.scheduler = scheduler_service

    def handle_event(self, event_data):
            try:
                e = json.loads(event_data)
                payload = e.get("payload", {})
                workflow_id = payload.get("workflow_id")
                if not workflow_id:
                    print("[WorkflowEventHandler] ⚠️ Missing workflow_id in event payload")
                    return

                event_type = e.get("type")

                if event_type == WORKFLOW_ACTIVATED:
                    print(f"[WorkflowEventHandler] ▶️ Activating workflow {workflow_id}")

                    for node in payload.get("nodes", []):
                        config = node.get("custom_config", {})
                        delay = config.get("delay_seconds", 0)
                        interval = config.get("interval_seconds", 10)
                        max_occurrences = config.get("max_occurrences")
                        until = config.get("until")
                        context = config.get("context")

                        next_run = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)

                        schedule = Schedule(
                            workflow_id=workflow_id,
                            interval_seconds=interval,
                            next_run=next_run,
                            context=context,
                            max_occurrences=max_occurrences,
                            until=until
                        )

                        self.scheduler.register_schedule(schedule)

                elif event_type in (WORKFLOW_DEACTIVATED, WORKFLOW_DELETED):
                    print(f"[WorkflowEventHandler] ⏹ Deactivating/deleting workflow {workflow_id}")
                    self.scheduler.remove_schedule(workflow_id)

                elif event_type == WORKFLOW_UPDATED:
                    print(f"[WorkflowEventHandler] 🔁 Updating schedule for workflow {workflow_id}")

                    for node in payload.get("nodes", []):
                        config = node.get("custom_config", {})
                        interval = config.get("interval_seconds", 10)
                        delay = config.get("delay_seconds", 0)
                        max_occurrences = config.get("max_occurrences")
                        until = config.get("until")
                        context = config.get("context")

                        next_run = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)

                        schedule = Schedule(
                            workflow_id=workflow_id,
                            interval_seconds=interval,
                            next_run=next_run,
                            context=context,
                            max_occurrences=max_occurrences,
                            until=until
                        )

                        # ✅ Update or replace existing schedule in Redis
                        self.scheduler.update_schedule(schedule)

            except Exception as ex:
                print(f"[WorkflowEventHandler] ❌ Error handling event: {ex}")