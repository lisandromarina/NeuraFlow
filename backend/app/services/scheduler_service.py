import json
import datetime
from models.schemas.schedule import Schedule

WORKFLOW_SCHEDULES_ZSET = "workflow_schedules_zset"
WORKFLOW_TRIGGERS_STREAM = "workflow_triggers"

class SchedulerService:
    def __init__(self, redis_repo):
        self.redis = redis_repo

    def register_schedule(self, schedule: Schedule):
        score = schedule.next_run.timestamp()
        self.redis.zadd(WORKFLOW_SCHEDULES_ZSET, {json.dumps(schedule.to_dict()): score})
        print(f"[SchedulerService] ✅ Registered schedule for workflow {schedule.workflow_id} at {schedule.next_run}")

    def remove_schedule(self, workflow_id):
        schedules = self.redis.zrange(WORKFLOW_SCHEDULES_ZSET, 0, -1)
        removed = False

        for raw in schedules:
            raw_str = raw.decode() if isinstance(raw, bytes) else raw
            try:
                data = json.loads(raw_str)
                if str(data.get("workflow_id")) == str(workflow_id):
                    self.redis.zrem(WORKFLOW_SCHEDULES_ZSET, raw)
                    removed = True
            except json.JSONDecodeError:
                continue

        if removed:
            print(f"[SchedulerService] ❌ Removed all schedules for workflow {workflow_id}")
        else:
            print(f"[SchedulerService] ⚠️ No schedules found to remove for workflow {workflow_id}")

    def update_schedule(self, schedule):
        # Remove old schedules for this workflow
        self.remove_schedule(schedule.workflow_id)

        # Register new schedule with updated interval
        self.register_schedule(schedule)

    def process_due_schedules(self):
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        due = self.redis.zrangebyscore(WORKFLOW_SCHEDULES_ZSET, 0, now_ts)

        for raw in due:
            raw_str = raw.decode() if isinstance(raw, bytes) else raw
            data = json.loads(raw_str)
            schedule = Schedule.from_dict(data)

            # Trigger workflow
            self.redis.xadd(WORKFLOW_TRIGGERS_STREAM, {
                "workflow_id": schedule.workflow_id,
                "context": json.dumps(schedule.context)
            })
            print(f"[SchedulerService] 🔔 Triggered workflow {schedule.workflow_id} (occurrence {schedule.occurrences + 1})")

            # Increment occurrences
            schedule.occurrences += 1
            stop = False

            if schedule.interval_seconds:
                # ✅ Use UTC-aware datetime
                next_run = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=schedule.interval_seconds)
                schedule.next_run = next_run

                # Handle 'until' safely
                if schedule.until:
                    try:
                        until_dt = datetime.datetime.fromisoformat(schedule.until.replace("Z", "+00:00"))
                        if next_run > until_dt:
                            stop = True
                    except Exception as e:
                        print(f"[SchedulerService] ⚠️ Failed to parse 'until' ({schedule.until}): {e}")
                        stop = True

                if schedule.max_occurrences and schedule.occurrences >= schedule.max_occurrences:
                    stop = True
            else:
                stop = True

            # Remove old schedule entry first
            self.redis.zrem(WORKFLOW_SCHEDULES_ZSET, raw_str)

            if not stop:
                self.redis.zadd(
                    WORKFLOW_SCHEDULES_ZSET,
                    {json.dumps(schedule.to_dict()): schedule.next_run.timestamp()}
                )
            else:
                print(f"[SchedulerService] 🏁 Schedule complete for workflow {schedule.workflow_id}")
