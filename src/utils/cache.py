import json
import hashlib
import asyncio
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import redis.asyncio as redis
from pydantic import BaseModel

class CacheConfig(BaseModel):
    redis_url: str = "redis://localhost:6379/0"
    ttl_seconds: int = 86400

class RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl_seconds: int = 86400):
        self.redis_url = redis_url
        self.ttl = ttl_seconds
        self.client = redis.from_url(redis_url, decode_responses=True)

    def _get_cache_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        cache_key = self._get_cache_key(key)
        try:
            cached_data = await self.client.get(cache_key)
            if not cached_data:
                return None
            cached = json.loads(cached_data)
            timestamp = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - timestamp > timedelta(seconds=self.ttl):
                await self.client.delete(cache_key)
                return None
            return cached['data']
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any):
        cache_key = self._get_cache_key(key)
        cached_data = {
            'timestamp': datetime.now().isoformat(),
            'data': value
        }
        try:
            await self.client.setex(cache_key, self.ttl, json.dumps(cached_data))
        except Exception as e:
            print(f"Cache set error: {e}")

def cache_result(ttl_seconds: int = 86400):
    def decorator(func: Callable):
        cache = RedisCache(ttl_seconds=ttl_seconds)
        
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result)
            return result
        return wrapper
    return decorator