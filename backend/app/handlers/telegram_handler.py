import json
import httpx
from handlers.base_node_handler import BaseNodeHandler
from services.redis_service import RedisService
from utils.token_security import decrypt_credentials
from config import settings


class TelegramTriggerHandler(BaseNodeHandler):
    def __init__(self, redis_service: RedisService):
        self.redis_service: RedisService = redis_service
        if not settings.ngrok_url:
            raise ValueError("Missing environment variable: NGROK_URL (required for Telegram webhooks)")
        # Remove trailing slash if present
        self.ngrok_url = settings.ngrok_url.rstrip('/')

    def _decrypt_bot_token(self, encrypted_token: str) -> str:
        """Decrypt the bot token from the encrypted format"""
        try:
            decrypted_data = decrypt_credentials(encrypted_token)
            return decrypted_data.get("token", "")
        except Exception as e:
            print(f"[TelegramHandler] Failed to decrypt bot_token: {e}")
            return ""

    def handle(self, node: dict, workflow_id: int):
        """
        Register a Telegram webhook for this workflow.
        Sets up the webhook with Telegram using the bot token from config.
        """
        config = node.get("custom_config", {})
        encrypted_bot_token = config.get("bot_token")
        
        if not encrypted_bot_token:
            print(f"[TelegramHandler] No bot_token found in config for workflow {workflow_id}")
            return
        
        # Decrypt the bot token
        bot_token = self._decrypt_bot_token(encrypted_bot_token)
        if not bot_token:
            print(f"[TelegramHandler] Failed to decrypt bot_token for workflow {workflow_id}")
            return
        
        # Construct webhook URL
        node_id = node.get('node_id') or node.get('id')  # Support both keys
        webhook_url = f"{self.ngrok_url}/telegram/webhook/{workflow_id}/{node_id}"
        
        # Register webhook with Telegram
        try:
            self._set_telegram_webhook(bot_token, webhook_url)
            print(f"[TelegramHandler] ✅ Registered webhook for workflow {workflow_id}, node {node_id} with URL: {webhook_url}")
        except Exception as e:
            print(f"[TelegramHandler] ❌ Failed to register webhook for workflow {workflow_id}, node {node_id}: {e}")

    def cleanup(self, node: dict, workflow_id: int):
        """
        Remove Telegram webhook when workflow is deleted/deactivated.
        """
        config = node.get("custom_config", {})
        encrypted_bot_token = config.get("bot_token")
        
        if not encrypted_bot_token:
            print(f"[TelegramHandler] No bot_token found for cleanup of workflow {workflow_id}")
            return
        
        # Decrypt the bot token
        bot_token = self._decrypt_bot_token(encrypted_bot_token)
        if not bot_token:
            print(f"[TelegramHandler] Failed to decrypt bot_token for cleanup of workflow {workflow_id}")
            return
        
        try:
            self._delete_telegram_webhook(bot_token)
            print(f"[TelegramHandler] ✅ Removed webhook for workflow {workflow_id}")
        except Exception as e:
            print(f"[TelegramHandler] ⚠️ Failed to remove webhook for workflow {workflow_id}: {e}")

    def _set_telegram_webhook(self, bot_token: str, webhook_url: str):
        """Set the webhook URL for a Telegram bot"""
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        with httpx.Client() as client:
            response = client.post(url, json={"url": webhook_url})
            response.raise_for_status()
            result = response.json()
            if not result.get("ok"):
                raise Exception(f"Telegram API error: {result.get('description')}")

    def _delete_telegram_webhook(self, bot_token: str):
        """Delete the webhook for a Telegram bot"""
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        with httpx.Client() as client:
            response = client.post(url, json={"drop_pending_updates": True})
            response.raise_for_status()

