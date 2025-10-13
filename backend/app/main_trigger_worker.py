from core.executor import WorkflowExecutor
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from services.user_credential_service import UserCredentialService
from services.trigger_worker import TriggerWorker
from dependencies import get_db_session
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")

if __name__ == "__main__":
    # get a DB session manually from the generator
    db = next(get_db_session())

    # --- Build executor
    executor = WorkflowExecutor(db)

    # --- Build user credential service manually
    repo = SqlAlchemyUserCredentialRepository(db)
    user_credential_service = UserCredentialService(repo)

    # --- Inject into services dict
    services = {
        "db": db,
        "user_credentials": user_credential_service,
    }

    # --- Build and run worker
    worker = TriggerWorker(executor, REDIS_URL, services=services)
    print("TriggerWorker listening...")
    worker.listen()