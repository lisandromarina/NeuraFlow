import redis, json, time, datetime

class SchedulerService:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.r = redis.Redis.from_url(redis_url)

    def register_schedule(
        self,
        workflow_id,
        start_time=None,           # first execution datetime
        interval_seconds=None,     # repeat interval
        until=None,                # ISO datetime string to stop
        max_occurrences=None,      # optional max runs
        context=None
    ):
        """Register a schedule. Nothing happens until this is called."""
        start_time = start_time or datetime.datetime.utcnow()
        data = {
            "workflow_id": workflow_id,
            "next_run": start_time.isoformat(),
            "context": context or {},
            "interval_seconds": interval_seconds,
            "until": until,
            "max_occurrences": max_occurrences,
            "occurrences": 0
        }
        self.r.hset("workflow_schedules", workflow_id, json.dumps(data))
        print(f"[SchedulerService] Registered workflow {workflow_id} to run at {start_time}")

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