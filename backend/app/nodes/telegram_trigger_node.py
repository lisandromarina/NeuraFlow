from core.node_factory import NodeFactory

@NodeFactory.register("TelegramTriggerNode")
class TelegramTriggerNodeExecutor:
    @staticmethod
    def get_trigger_metadata(config):
        """Return telegram webhook metadata for registration"""
        return {
            "bot_token": config.get("bot_token"),
            "workflow_id": config.get("workflow_id"),
        }

    @staticmethod
    def run(config, context):
        # This should never run at runtime
        raise RuntimeError("TelegramTriggerNode is a trigger and should not execute at runtime")

