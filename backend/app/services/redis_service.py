import json
from redis import Redis # type: ignore
from datetime import datetime

class RedisService:
    def __init__(self, redis_client: Redis, channel_name: str = "workflow_events"):
        self.redis_client = redis_client
        self.channel_name = channel_name

    def publish_event(self, event_type: str, payload: dict):
        """
        Publishes a structured event to Redis with standardized metadata.
        """
        message = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
        }
        self.redis_client.publish(self.channel_name, json.dumps(message))
