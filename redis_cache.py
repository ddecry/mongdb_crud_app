# redis_cache.py
import os
import json
from redis import Redis
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))  # tempo em segundos

class RedisCache:
    def __init__(self, url=REDIS_URL):
        self.client = Redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> Optional[dict]:
        value = self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return None

    def set(self, key: str, data, ttl=CACHE_TTL_SECONDS):
        s = json.dumps(data, ensure_ascii=False)
        self.client.setex(key, ttl, s)

    def delete(self, key: str):
        self.client.delete(key)
