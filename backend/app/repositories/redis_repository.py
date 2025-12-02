import redis
from config import settings

class RedisRepository:
    def __init__(self, redis_url=None):
        if redis_url:
            self.r = redis.Redis.from_url(redis_url)
        else:
            self.r = redis.Redis.from_url(settings.redis_url)

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
