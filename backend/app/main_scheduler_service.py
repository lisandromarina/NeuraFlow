import os
from repositories.redis_repository import RedisRepository
from services.scheduler_runner import SchedulerRunner
from services.workflow_event_handler import WorkflowEventHandler
from services.scheduler_service import SchedulerService
from services.node_processor_service import NodeProcessorService  # renamed service

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")

if __name__ == "__main__":
    # Redis repo
    redis_repo = RedisRepository(REDIS_URL)
    print("Hello")
    # Core services
    scheduler_service = SchedulerService(redis_repo)
    # event_click_service = EventClickService(...)  # optional for other categories

    # Node processor service (delegates nodes to the correct handler)
    node_processor_service = NodeProcessorService(
        scheduler_service=scheduler_service,
        # event_service=event_click_service  # optional
    )

    # Workflow event handler
    event_handler = WorkflowEventHandler(
        node_processor_service=node_processor_service,
        scheduler_service=scheduler_service
    )

    # Runner
    runner = SchedulerRunner(
        scheduler_service=scheduler_service,
        event_handler=event_handler,
        redis_repo=redis_repo
    )

    runner.run_forever()
