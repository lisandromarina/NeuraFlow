from core.node_factory import NodeFactory

@NodeFactory.register("SchedulerNode")
class SchedulerNodeExecutor:
    @staticmethod
    def get_trigger_metadata(config):
        """Return cron expression from config for workflow registration"""
        return {
            "cron": config.get("cron"),
        }

    @staticmethod
    def run(config, context):
        # This should never run at runtime
        raise RuntimeError("SchedulerNode is a trigger and should not execute at runtime")
