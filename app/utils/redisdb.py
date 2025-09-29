import redis
from typing import Optional

class RedisDB:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection"""
        self.redis_url = redis_url
        self.client = None
        self._connect()
    
    def _connect(self):
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            print(f"✅ Connected to Redis at {self.redis_url}")
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise
    
    def ping(self) -> bool:
        try:
            response = self.client.ping()
            if response:
                print("✅ Redis ping successful!")
                return True
            return False
        except Exception as e:
            print(f"❌ Redis ping failed: {e}")
            return False
    
    def flush_memory(self):
        try:
            self.client.flushdb()
            print("✅ Redis memory flushed successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to flush Redis memory: {e}")
            return False
    
    def get_info(self) -> dict:
        try:
            info = self.client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_keys': self.client.dbsize()
            }
        except Exception as e:
            print(f"❌ Failed to get Redis info: {e}")
            return {}
    
    def close(self):
        if self.client:
            self.client.close()
            print("✅ Redis connection closed")