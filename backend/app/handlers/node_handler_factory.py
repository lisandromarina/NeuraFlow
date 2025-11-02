from handlers.base_node_handler import BaseNodeHandler
from handlers.scheduler_handler import SchedulerNodeHandler
from handlers.telegram_handler import TelegramTriggerHandler


class NodeHandlerFactory:
    def __init__(self, scheduler_service, redis_service):
        self.handlers = {
            "SchedulerNode": SchedulerNodeHandler(scheduler_service),
            "TelegramTriggerNode": TelegramTriggerHandler(redis_service),
        }

    def get_handler(self, category: str) -> BaseNodeHandler:
        return self.handlers.get(category)
