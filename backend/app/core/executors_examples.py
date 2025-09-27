# engine/executors.py
from .node_factory import NodeFactory

# Webhook node
@NodeFactory.register("baseHandle")
class WebhookExecutor:
    def run(self, config, context):
        print(f"Webhook called with URL: {config.get('url')}")
        return {"status": "success"}

# Send Email node
@NodeFactory.register("SendEmail")
class SendEmailExecutor:
    def run(self, config, context):
        print(f"Sending email: {config.get('template')}")
        return {"status": "sent"}

# Decision node (control flow)
@NodeFactory.register("DecisionNode")
class DecisionNodeExecutor:
    def run(self, config, context):
        variable_name = config.get("variable")
        value = context.get(variable_name)
        print(f"Decision node: {variable_name} = {value}")
        return {"status": value}
