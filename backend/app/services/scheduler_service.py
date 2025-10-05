import os
import redis
import json
import time
import datetime

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")

WORKFLOW_EVENT_CHANNEL = "workflow_events"
WORKFLOW_SCHEDULES_ZSET = "workflow_schedules_zset"
WORKFLOW_TRIGGERS_STREAM = "workflow_triggers"


class SchedulerService:
    def __init__(self, redis_url=None):
        self.r = redis.Redis.from_url(redis_url or REDIS_URL)
        self.pubsub = self.r.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(WORKFLOW_EVENT_CHANNEL)

    def register_schedule(
        self,
        workflow_id,
        start_time=None,
        interval_seconds=None,
        until=None,
        max_occurrences=None,
        context=None,
    ):
        start_time = start_time or datetime.datetime.utcnow()

        data = {
            "workflow_id": workflow_id,
            "next_run": start_time.isoformat(),
            "interval_seconds": interval_seconds,
            "until": until,
            "max_occurrences": max_occurrences,
            "occurrences": 0,
            "context": context or {},
        }

        score = start_time.timestamp()
        self.r.zadd(WORKFLOW_SCHEDULES_ZSET, {json.dumps(data): score})
        print(f"[SchedulerService] ✅ Registered schedule for workflow {workflow_id} at {start_time}")

    def remove_schedule(self, workflow_id):
        schedules = self.r.zrange(WORKFLOW_SCHEDULES_ZSET, 0, -1)
        for raw in schedules:
            # decode bytes to string
            raw_str = raw.decode() if isinstance(raw, bytes) else raw
            data = json.loads(raw_str)

            if str(data["workflow_id"]) == str(workflow_id):
                self.r.zrem(WORKFLOW_SCHEDULES_ZSET, raw)
                print(f"[SchedulerService] ❌ Removed schedule for workflow {workflow_id}")

    def process_due_schedules(self):
        now_ts = datetime.datetime.utcnow().timestamp()
        due = self.r.zrangebyscore(WORKFLOW_SCHEDULES_ZSET, 0, now_ts)

        for raw in due:
            data = json.loads(raw)
            workflow_id = data["workflow_id"]

            self.r.xadd(WORKFLOW_TRIGGERS_STREAM, {
                "workflow_id": workflow_id,
                "context": json.dumps(data.get("context", {}))
            })
            print(f"[SchedulerService] 🔔 Triggered workflow {workflow_id}")

            data["occurrences"] = data.get("occurrences", 0) + 1
            interval = data.get("interval_seconds")
            until = data.get("until")
            max_occ = data.get("max_occurrences")

            stop = False
            if interval:
                next_run = datetime.datetime.utcnow() + datetime.timedelta(seconds=interval)
                data["next_run"] = next_run.isoformat()

                if until and next_run > datetime.datetime.fromisoformat(until):
                    stop = True
                if max_occ and data["occurrences"] >= max_occ:
                    stop = True
            else:
                stop = True

            self.r.zrem(WORKFLOW_SCHEDULES_ZSET, raw)
            if not stop:
                self.r.zadd(WORKFLOW_SCHEDULES_ZSET, {
                    json.dumps(data): datetime.datetime.fromisoformat(data["next_run"]).timestamp()
                })

    def handle_workflow_event(self, event_data):
        try:
            e = json.loads(event_data)
            payload = e.get("payload", {})
            workflow_id = payload.get("workflow_id")

            if not workflow_id:
                print("[SchedulerService] ⚠️ Missing workflow_id in event payload")
                return

            event_type = e.get("type")
            if event_type == "workflow_activated":
                print(f"[SchedulerService] ▶️ Activating workflow {workflow_id}")
                for node in payload.get("nodes", []):
                    self.register_schedule(
                        workflow_id=workflow_id,
                        interval_seconds=node.get("interval_seconds", 10),  # fallback
                        start_time=datetime.datetime.utcnow(),
                        context=node.get("context")
                    )

            elif event_type in ("workflow_deactivated", "workflow_deleted"):
                print(f"[SchedulerService] ⏹ Deactivating/deleting workflow {workflow_id}")
                self.remove_schedule(workflow_id)

        except Exception as ex:
            print(f"[SchedulerService] ❌ Error handling event: {ex}")

    def run_forever(self):
        print("[SchedulerService] 🕓 Scheduler running...")
        last_pubsub_check = time.time()

        while True:
            # 1️⃣ Process due schedules every loop
            self.process_due_schedules()

            # 2️⃣ Non-blocking check for Redis Pub/Sub messages
            if time.time() - last_pubsub_check >= 0.5:
                message = self.pubsub.get_message(timeout=0.1)
                if message and message.get("type") == "message":
                    self.handle_workflow_event(message["data"])
                last_pubsub_check = time.time()

            time.sleep(1)
