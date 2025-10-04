import os
import redis, json, time, datetime

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")

class SchedulerService:
    def __init__(self, redis_url=None):
        self.r = redis.Redis.from_url(redis_url or REDIS_URL)

    def register_schedule(
        self,
        workflow_id,
        start_time=None,
        interval_seconds=None,
        until=None,
        max_occurrences=None,
        context=None
    ):
    
        """Register or update a schedule."""
        start_time = start_time or datetime.datetime.utcnow()
        workflow_id_str = str(workflow_id)
        existing = self.r.hget("workflow_schedules", workflow_id_str)
        if existing:
            # Merge existing schedule with updates
            data = json.loads(existing)
            print(f"[SchedulerService] Updating existing schedule for {workflow_id}")
        else:
            data = {"occurrences": 0}
            print(f"[SchedulerService] Creating new schedule for {workflow_id}")

        # Update/override relevant fields
        data.update({
            "workflow_id": workflow_id,
            "next_run": start_time.isoformat(),
            "context": context or data.get("context", {}),
            "interval_seconds": interval_seconds,
            "until": until,
            "max_occurrences": max_occurrences,
        })

        self.r.hset("workflow_schedules", workflow_id, json.dumps(data))
        print(f"[SchedulerService] Schedule for {workflow_id} set to run at {start_time}")

    def run_forever(self):
        """Main loop — triggers only registered schedules"""
        while True:
            now = datetime.datetime.utcnow()
            schedules = self.r.hgetall("workflow_schedules")

            for wf_id, raw in schedules.items():
                data = json.loads(raw)
                next_run = datetime.datetime.fromisoformat(data["next_run"])

                if now >= next_run:
                    # Push trigger to Redis stream
                    self.r.xadd("workflow_triggers", {
                        "workflow_id": data["workflow_id"],
                        "context": json.dumps(data["context"])
                    })
                    data["occurrences"] = data.get("occurrences", 0) + 1
                    print(f"[SchedulerService] Triggered workflow {data['workflow_id']} at {now}")

                    # Determine next_run
                    interval = data.get("interval_seconds")
                    until = data.get("until")
                    max_occ = data.get("max_occurrences")

                    # Remove if one-shot or end conditions reached
                    stop = False
                    if interval:
                        next_run_time = now + datetime.timedelta(seconds=interval)
                        if until and next_run_time > datetime.datetime.fromisoformat(until):
                            stop = True
                        if max_occ and data["occurrences"] >= max_occ:
                            stop = True
                        if not stop:
                            data["next_run"] = next_run_time.isoformat()
                    else:
                        # One-shot
                        stop = True

                    if stop:
                        self.r.hdel("workflow_schedules", wf_id)
                    else:
                        self.r.hset("workflow_schedules", wf_id, json.dumps(data))

            time.sleep(1)

    def delete_redis(self):
        self.r.flushall()
        print("All keys deleted from all Redis databases")
