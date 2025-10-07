from handlers.base_node_handler import BaseNodeHandler
from handlers.scheduler_handler import SchedulerNodeHandler


class NodeHandlerFactory:
    def __init__(self, scheduler_service):
        self.handlers = {
            "SchedulerService": SchedulerNodeHandler(scheduler_service),
        }

    def get_handler(self, category: str) -> BaseNodeHandler:
        return self.handlers.get(category)
