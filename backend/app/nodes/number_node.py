from core.node_factory import NodeFactory

@NodeFactory.register("baseHandle")
class WebhookExecutor:
    def run(self, config, context):

        return 3
    
