from fastapi import APIRouter, Depends, HTTPException, Request
from dependencies import get_redis_client, get_workflow_node_repository, get_db_session
from services.redis_service import RedisService
from services.telegram_service import TelegramService
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from auth_dependencies import get_current_user, verify_workflow_ownership
from sqlalchemy.orm import Session # type: ignore
from redis import Redis

router = APIRouter(prefix="/telegram", tags=["Telegram"])


def get_telegram_service(
    workflow_node_repo: SqlAlchemyWorkflowNodeRepository = Depends(get_workflow_node_repository),
    redis_client: Redis = Depends(get_redis_client)
) -> TelegramService:
    """Dependency to provide TelegramService instance"""
    redis_service = RedisService(redis_client)
    return TelegramService(workflow_node_repo, redis_service)


@router.get("/webhook-info/{workflow_id}/{node_id}")
def get_webhook_info(
    workflow_id: int,
    node_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: TelegramService = Depends(get_telegram_service)
):
    """
    Get webhook information for a Telegram bot.
    Returns the current webhook URL and status from Telegram.
    Requires ownership of the workflow.
    """
    # Verify ownership of the workflow
    verify_workflow_ownership(workflow_id, current_user, db)
    
    try:
        return service.get_webhook_info(workflow_id, node_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching webhook info: {str(e)}")


@router.post("/webhook/{workflow_id}/{node_id}")
async def telegram_webhook(
    workflow_id: int,
    node_id: int,
    request: Request,
    service: TelegramService = Depends(get_telegram_service)
):
    """
    Receives Telegram webhook messages and triggers the associated workflow.
    This endpoint is called by Telegram when a message is received by the bot.
    """
    try:
        # Parse the incoming update from Telegram
        update_data = await request.json()
        
        return service.process_webhook(workflow_id, node_id, update_data)
        
    except Exception as e:
        print(f"[TelegramWebhook] ❌ Error processing webhook: {e}")
        # Return 200 to Telegram so it doesn't retry
        return {"ok": False, "error": str(e)}

