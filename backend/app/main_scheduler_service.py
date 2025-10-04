import os
from services.scheduler_service import SchedulerService

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")

if __name__ == "__main__":
    sched = SchedulerService(REDIS_URL)
    print("SchedulerService")
    sched.run_forever()