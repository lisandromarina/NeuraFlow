import redis
import os

class RedisRepository:
    def __init__(self, redis_url=None):
        self.r = redis.Redis.from_url(redis_url or os.getenv("REDIS_URL", "redis://redis_db:6379/0"))

    def zadd(self, key, mapping):
        self.r.zadd(key, mapping)

    def zrange(self, key, start, end):
        return self.r.zrange(key, start, end)

    def zrangebyscore(self, key, min_score, max_score):
        return self.r.zrangebyscore(key, min_score, max_score)

    def zrem(self, key, value):
        self.r.zrem(key, value)

    def xadd(self, stream, mapping):
        self.r.xadd(stream, mapping)

    def pubsub(self, **kwargs):
        return self.r.pubsub(**kwargs)
