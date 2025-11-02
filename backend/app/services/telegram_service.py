import json
import httpx
from typing import Dict, Optional
from fastapi import HTTPException
from utils.token_security import decrypt_credentials
from repositories.sqlalchemy_workflow_node_repository import SqlAlchemyWorkflowNodeRepository
from services.redis_service import RedisService

WORKFLOW_TRIGGERS_STREAM = "workflow_triggers"


class TelegramService:
    def __init__(
        self,
        workflow_node_repo: SqlAlchemyWorkflowNodeRepository,
        redis_service: RedisService
    ):
        self.workflow_node_repo = workflow_node_repo
        self.redis_service = redis_service

    def get_webhook_info(self, workflow_id: int, node_id: int) -> Dict:
        """
        Get webhook information for a Telegram bot.
        Returns the current webhook URL and status from Telegram.
        """
        # Get the workflow node
        workflow_node = self.workflow_node_repo.get_by_id(node_id)
        
        if not workflow_node or workflow_node.workflow_id != workflow_id:
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

    def process_webhook(self, workflow_id: int, node_id: int, update_data: Dict) -> Dict:
        """
        Receives Telegram webhook messages and triggers the associated workflow.
        This method processes incoming updates from Telegram and publishes them to Redis.
        """
        # Extract message data
        message = update_data.get("message", {})
        if not message:
            # This might be an edited message or other update type
            print(f"[TelegramService] Received non-message update: {update_data}")
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
        
        print(f"[TelegramService] Received message for workflow {workflow_id}, node {node_id}")
        print(f"[TelegramService] Message: {message.get('text', 'No text')}")
        
        # Add to Redis stream to trigger workflow
        self.redis_service.add_to_stream(WORKFLOW_TRIGGERS_STREAM, {
            "workflow_id": str(workflow_id),
            "context": json.dumps(context)
        })
        
        print(f"[TelegramService] ✅ Triggered workflow {workflow_id} via Redis stream")
        
        return {"ok": True}

