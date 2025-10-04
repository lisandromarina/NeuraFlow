from core.executor import WorkflowExecutor
from services.trigger_worker import TriggerWorker
from dependencies import get_db_session
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")

if __name__ == "__main__":
    # get a DB session manually from the generator
    db = next(get_db_session())

    executor = WorkflowExecutor(db)
    worker = TriggerWorker(executor, REDIS_URL)
    print("TriggerWorker listening...")
    worker.listen()
