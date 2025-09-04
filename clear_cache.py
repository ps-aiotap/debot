#!/usr/bin/env python3

import redis
import os
from dotenv import load_dotenv

load_dotenv()

def clear_all_caches():
    """Clear Redis cache and print status."""
    try:
        # Connect to Redis
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True
        )
        
        # Clear all cache
        redis_client.flushdb()
        print("✅ Redis cache cleared successfully")
        
        # Show cache stats
        info = redis_client.info()
        print(f"📊 Redis memory used: {info.get('used_memory_human', 'Unknown')}")
        print(f"📊 Connected clients: {info.get('connected_clients', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Failed to clear Redis cache: {e}")

if __name__ == "__main__":
    clear_all_caches()