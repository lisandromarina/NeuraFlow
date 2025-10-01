# engine/executors.py
from .node_factory import NodeFactory
import time

# Webhook node
@NodeFactory.register("baseHandle")
class WebhookExecutor:
    def run(self, config, context):

        return 3
    
    
@NodeFactory.register("MultiplyNode")
class MultiplyExecutor:
    @staticmethod
    def run(config, context):
        """
        This node multiplies the parent_result by a config value.
        Expects:
          - context["parent_result"] (direct parent output)
          - config["multiplier"]
        """

        parent_output = context.get("parent_result", 1)

        multiplier = config.get("factorB", 1)
        result = parent_output * multiplier

        print(f"[MultiplyNode] Parent Result: {parent_output}, Multiplier: {multiplier}, Result: {result}")
        return result

# Send Email node
@NodeFactory.register("SendEmail")
class SendEmailExecutor:
    def run(self, config, context):
        print("Context in email sender: ")
        print(context)
        return {"status": "sent"}

# Decision node (control flow)
@NodeFactory.register("DecisionNode")
class DecisionNodeExecutor:
    def run(self, config, context):
        variable_name = config.get("variable")
        value = context.get(variable_name)
        print(f"Decision node: {variable_name} = {value}")
        return {"status": value}
