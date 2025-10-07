import datetime
from services.scheduler_service import SchedulerService
from handlers.base_node_handler import BaseNodeHandler
from models.schemas.schedule import Schedule


class SchedulerNodeHandler(BaseNodeHandler):
    def __init__(self, scheduler_service: SchedulerService):
        self.scheduler: SchedulerService = scheduler_service

    def handle(self, node: dict, workflow_id: int):
        config = node.get("custom_config", {})
        next_run = datetime.datetime.utcnow() + datetime.timedelta(seconds=config.get("delay_seconds", 0))
        schedule = Schedule(
            workflow_id=workflow_id,
            interval_seconds=config.get("interval_seconds", 10),
            next_run=next_run,
            context=config.get("context"),
            max_occurrences=config.get("max_occurrences"),
            until=config.get("until"),
        )
        self.scheduler.update_schedule(schedule)

    def cleanup(self, node: dict, workflow_id: int):
        """Called on workflow deletion/deactivation"""
        self.scheduler.remove_schedule(workflow_id)