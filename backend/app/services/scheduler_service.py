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
        for raw in schedules:
            raw_str = raw.decode() if isinstance(raw, bytes) else raw
            data = json.loads(raw_str)
            if str(data["workflow_id"]) == str(workflow_id):
                self.redis.zrem(WORKFLOW_SCHEDULES_ZSET, raw)
                print(f"[SchedulerService] ❌ Removed schedule for workflow {workflow_id}")

    def process_due_schedules(self):
        now_ts = datetime.datetime.utcnow().timestamp()
        due = self.redis.zrangebyscore(WORKFLOW_SCHEDULES_ZSET, 0, now_ts)

        for raw in due:
            data = json.loads(raw)
            schedule = Schedule.from_dict(data)

            # Trigger workflow
            self.redis.xadd(WORKFLOW_TRIGGERS_STREAM, {
                "workflow_id": schedule.workflow_id,
                "context": json.dumps(schedule.context)
            })
            print(f"[SchedulerService] 🔔 Triggered workflow {schedule.workflow_id}")

            # Update schedule
            schedule.occurrences += 1
            stop = False

            if schedule.interval_seconds:
                next_run = datetime.datetime.utcnow() + datetime.timedelta(seconds=schedule.interval_seconds)
                schedule.next_run = next_run
                if schedule.until and next_run > datetime.datetime.fromisoformat(schedule.until):
                    stop = True
                if schedule.max_occurrences and schedule.occurrences >= schedule.max_occurrences:
                    stop = True
            else:
                stop = True

            self.redis.zrem(WORKFLOW_SCHEDULES_ZSET, raw)
            if not stop:
                self.redis.zadd(WORKFLOW_SCHEDULES_ZSET, {json.dumps(schedule.to_dict()): schedule.next_run.timestamp()})
