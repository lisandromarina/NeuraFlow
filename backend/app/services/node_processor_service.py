from handlers.node_handler_factory import NodeHandlerFactory
from services.redis_service import RedisService


class NodeProcessorService:
    def __init__(self, scheduler_service, redis_service: RedisService):
        self.factory = NodeHandlerFactory(scheduler_service, redis_service)

    def process(self, node: dict, workflow_id: int):
        category = node.get("node_category")
        handler = self.factory.get_handler(category)
        if handler:
            handler.handle(node, workflow_id)

    def remove(self, node: dict, workflow_id: int):
        """Handle deletion / deactivation of a node"""
        category = node.get("node_category")
        handler = self.factory.get_handler(category)
        handler.cleanup(node, workflow_id)
