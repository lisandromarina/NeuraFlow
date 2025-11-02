from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict
import json
import httpx
from dependencies import get_db_session, get_redis_client
from sqlalchemy.orm import Session
from models.db_models.workflow_nodes import WorkflowNode
from utils.token_security import decrypt_credentials
from services.redis_service import RedisService
from redis import Redis

router = APIRouter(prefix="/telegram", tags=["Telegram"])

WORKFLOW_TRIGGERS_STREAM = "workflow_triggers"


def get_redis_service(redis_client: Redis = Depends(get_redis_client)) -> RedisService:
    """Dependency to provide RedisService instance"""
    return RedisService(redis_client)


@router.get("/webhook-info/{workflow_id}/{node_id}")
def get_webhook_info(
    workflow_id: int,
    node_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Get webhook information for a Telegram bot.
    Returns the current webhook URL and status from Telegram.
    """
    try:
        # Get the workflow node
        workflow_node = db.query(WorkflowNode).filter(
            WorkflowNode.id == node_id,
            WorkflowNode.workflow_id == workflow_id
        ).first()
        
        if not workflow_node:
            raise HTTPException(status_code=404, detail="Workflow node not found")
        
        # Get the bot token from config
        config = workflow_node.custom_config or {}
        encrypted_bot_token = config.get("bot_token")
        
        if not encrypted_bot_token:
            raise HTTPException(status_code=400, detail="No bot token configured for this node")
        
        # Decrypt the bot token
        try:
            decrypted_data = decrypt_credentials(encrypted_bot_token)
            bot_token = decrypted_data.get("token", "")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to decrypt bot token: {str(e)}")
        
        if not bot_token:
            raise HTTPException(status_code=400, detail="Invalid bot token")
        
        # Get webhook info from Telegram
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            webhook_info = response.json()
        
        return webhook_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching webhook info: {str(e)}")


@router.post("/webhook/{workflow_id}/{node_id}")
async def telegram_webhook(
    workflow_id: int,
    node_id: int,
    request: Request,
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Receives Telegram webhook messages and triggers the associated workflow.
    This endpoint is called by Telegram when a message is received by the bot.
    """
    try:
        # Parse the incoming update from Telegram
        update_data = await request.json()
        
        # Extract message data
        message = update_data.get("message", {})
        if not message:
            # This might be an edited message or other update type
            print(f"[TelegramWebhook] Received non-message update: {update_data}")
            return {"ok": True}
        
        # Build context with message data
        chat_data = message.get("chat", {})
        chat_id = chat_data.get("id")
        text = message.get("text")
        
        context = {
            "message": message,
            "chat_id": chat_id,
            "text": text,
            "from_user": message.get("from"),
            "chat": chat_data,
            "date": message.get("date"),
            "update": update_data,
        }
        
        print(f"[TelegramWebhook] Received message for workflow {workflow_id}, node {node_id}")
        print(f"[TelegramWebhook] Message: {message.get('text', 'No text')}")
        
        # Add to Redis stream to trigger workflow
        redis_service.add_to_stream(WORKFLOW_TRIGGERS_STREAM, {
            "workflow_id": str(workflow_id),
            "context": json.dumps(context)
        })
        
        print(f"[TelegramWebhook] ✅ Triggered workflow {workflow_id} via Redis stream")
        
        return {"ok": True}
        
    except Exception as e:
        print(f"[TelegramWebhook] ❌ Error processing webhook: {e}")
        # Return 200 to Telegram so it doesn't retry
        return {"ok": False, "error": str(e)}

