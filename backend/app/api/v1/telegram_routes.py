from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict
import json
import redis
import os
import httpx
from dependencies import get_db_session
from sqlalchemy.orm import Session
from models.db_models.workflow_nodes import WorkflowNode
from utils.token_security import decrypt_credentials

router = APIRouter(prefix="/telegram", tags=["Telegram"])

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("Missing environment variable: REDIS_URL")

redis_client = redis.Redis.from_url(REDIS_URL)
WORKFLOW_TRIGGERS_STREAM = "workflow_triggers"


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
    db: Session = Depends(get_db_session)
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
        redis_client.xadd(WORKFLOW_TRIGGERS_STREAM, {
            "workflow_id": str(workflow_id),
            "context": json.dumps(context)
        })
        
        print(f"[TelegramWebhook] ✅ Triggered workflow {workflow_id} via Redis stream")
        
        return {"ok": True}
        
    except Exception as e:
        print(f"[TelegramWebhook] ❌ Error processing webhook: {e}")
        # Return 200 to Telegram so it doesn't retry
        return {"ok": False, "error": str(e)}

