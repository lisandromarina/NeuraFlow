from core.logger import Logger
from core.executor import WorkflowExecutor
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from services.user_credential_service import UserCredentialService
from services.trigger_worker import TriggerWorker
from dependencies import get_db_session
from config import settings
import nodes # Do not delete, important for loading nodes!

if __name__ == "__main__":
    # get a DB session manually from the generator
    db = next(get_db_session())
    logger = Logger("[TriggerWorker]")
    # --- Build executor
    executor = WorkflowExecutor(db, logger=logger)

    # --- Build user credential service manually
    repo = SqlAlchemyUserCredentialRepository(db)
    user_credential_service = UserCredentialService(repo)

    # --- Inject into services dict
    services = {
        "db": db,
        "user_credentials": user_credential_service,
        "logger": logger
    }

    # --- Build and run worker
    worker = TriggerWorker(executor, settings.redis_url, services=services)
    logger.log("TriggerWorker listening...")
    worker.listen()