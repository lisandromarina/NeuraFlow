from core.logger import Logger
from core.executor import WorkflowExecutor
import redis, json, os

class TriggerWorker:
    def __init__(
        self,
        executor: WorkflowExecutor,
        redis_url="redis://localhost:6379/0",
        group_name="workflow_group",
        consumer_name=None,
        services=None
    ):
        self.executor = executor
        self.r = redis.Redis.from_url(redis_url)
        self.stream_name = "workflow_triggers"
        self.group_name = group_name
        self.consumer_name = consumer_name or f"consumer-{os.getpid()}"
        self.services = services or {}  # ✅ injected services

        # create group if not exists
        try:
            self.r.xgroup_create(self.stream_name, self.group_name, id="0", mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

    def listen(self):
        logger: Logger = self.services.get("logger")
        logger.log(f"Listening as {self.consumer_name}...")
        while True:
            msgs = self.r.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={self.stream_name: ">"},
                count=1,
                block=5000
            )

            if not msgs:
                logger.log("No messages yet...")
                continue

            for stream, entries in msgs:
                for entry_id, fields in entries:
                    workflow_id = int(fields[b'workflow_id'])
                    context = json.loads(fields[b'context'])

                    # ✅ Inject shared services
                    context["services"] = {**context.get("services", {}), **self.services}

                    try:
                        logger.log(f"Executing workflow {workflow_id}")
                        self.executor.execute_workflow(workflow_id, context)
                        self.r.xack(self.stream_name, self.group_name, entry_id)
                        logger.log(f"Workflow {workflow_id} done, acked {entry_id}")
                    except Exception as e:
                        logger.log(f"Workflow {workflow_id} failed: {e}")
