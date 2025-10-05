import os
from repositories.redis_repository import RedisRepository
from services.scheduler_runner import SchedulerRunner
from services.workflow_event_handler import WorkflowEventHandler
from services.scheduler_service import SchedulerService

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")

if __name__ == "__main__":
    redis_repo = RedisRepository(REDIS_URL)
    scheduler_service = SchedulerService(redis_repo)
    event_handler = WorkflowEventHandler(scheduler_service)
    runner = SchedulerRunner(scheduler_service, event_handler, redis_repo)
    runner.run_forever()