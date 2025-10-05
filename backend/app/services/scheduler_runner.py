import time
from repositories.redis_repository import RedisRepository

WORKFLOW_EVENT_CHANNEL = "workflow_events"

class SchedulerRunner:
    def __init__(self, scheduler_service, event_handler, redis_repo: RedisRepository):
        self.scheduler = scheduler_service
        self.event_handler = event_handler
        self.pubsub = redis_repo.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(WORKFLOW_EVENT_CHANNEL)

    def run_forever(self):
        print("[SchedulerRunner] 🕓 Scheduler running...")
        last_pubsub_check = time.time()

        while True:
            # Process due schedules
            self.scheduler.process_due_schedules()

            # Check pub/sub messages periodically
            if time.time() - last_pubsub_check >= 0.5:
                message = self.pubsub.get_message(timeout=0.1)

                if message and message.get("type") == "message":
                    data = message["data"]
                    # ✅ DECODE BYTES HERE
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    self.event_handler.handle_event(data)

                last_pubsub_check = time.time()

            time.sleep(1)
