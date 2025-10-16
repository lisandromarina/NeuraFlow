import time
import json
from services.workflow_event_handler import WorkflowEventHandler
from services.scheduler_service import SchedulerService
from repositories.redis_repository import RedisRepository

WORKFLOW_EVENT_CHANNEL = "workflow_events"

class SchedulerRunner:
    def __init__(
            self, 
            scheduler_service: SchedulerService, 
            event_handler: WorkflowEventHandler, 
            redis_repo: RedisRepository
        ):
        self.scheduler = scheduler_service
        self.event_handler = event_handler
        self.pubsub = redis_repo.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(WORKFLOW_EVENT_CHANNEL)

    def run_forever(self):
        print("[SchedulerRunner]  Scheduler running...")
        last_pubsub_check = time.time()

        while True:
            # 1️⃣ Process due schedules
            self.scheduler.process_due_schedules()

            # 2️⃣ Check pub/sub messages periodically
            if time.time() - last_pubsub_check >= 0.5:
                message = self.pubsub.get_message(timeout=0.1)

                if message and message.get("type") == "message":
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    print("[SchedulerRunner] Received message:", data) 
                    # Parse JSON and separate type & payload
                    try:
                        event = json.loads(data)
                        event_type = event.get("type")
                        payload = event.get("payload", {})

                        # Delegate to event handler
                        print("[SchedulerRunner] BEFORE") 
                        self.event_handler.handle_event(event_type, payload)

                    except json.JSONDecodeError:
                        print("[SchedulerRunner]  Failed to decode message:", data)

                last_pubsub_check = time.time()

            time.sleep(1)