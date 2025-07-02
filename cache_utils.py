import redis
import json
import hashlib
import os
import pickle
from typing import Optional, Any, List
from dotenv import load_dotenv

load_dotenv()

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

# Binary Redis client for embeddings
redis_binary_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=False
)

def generate_cache_key(query: str, context_data: Any, model: str) -> str:
    """Generate a cache key for LLM responses."""
    content = f"{query}:{json.dumps(context_data, sort_keys=True)}:{model}"
    return f"llm_response:{hashlib.md5(content.encode()).hexdigest()}"

def get_cached_response(query: str, context_data: Any, model: str) -> Optional[str]:
    """Get cached LLM response."""
    try:
        cache_key = generate_cache_key(query, context_data, model)
        return redis_client.get(cache_key)
    except Exception:
        return None

def cache_response(query: str, context_data: Any, model: str, response: str, ttl: int = 3600):
    """Cache LLM response with TTL (default 1 hour)."""
    try:
        cache_key = generate_cache_key(query, context_data, model)
        redis_client.setex(cache_key, ttl, response)
    except Exception:
        pass  # Fail silently if caching fails

def generate_content_hash(content: str) -> str:
    """Generate hash for content to use as cache key."""
    return hashlib.sha256(content.encode()).hexdigest()

def cache_embedding(content: str, embedding: List[float], ttl: int = None) -> None:
    """Cache embedding vector for content."""
    try:
        content_hash = generate_content_hash(content)
        cache_key = f"embedding:{content_hash}"
        ttl = ttl or int(os.getenv("EMBEDDING_CACHE_TTL", 86400))
        redis_binary_client.setex(cache_key, ttl, pickle.dumps(embedding))
    except Exception:
        pass

def get_cached_embedding(content: str) -> Optional[List[float]]:
    """Get cached embedding for content."""
    try:
        content_hash = generate_content_hash(content)
        cache_key = f"embedding:{content_hash}"
        cached = redis_binary_client.get(cache_key)
        return pickle.loads(cached) if cached else None
    except Exception:
        return None

def cache_crawled_content(url: str, content: str, ttl: int = 86400) -> None:
    """Cache crawled web content."""
    try:
        cache_key = f"crawl:{hashlib.md5(url.encode()).hexdigest()}"
        redis_client.setex(cache_key, ttl, content)
    except Exception:
        pass

def get_cached_crawled_content(url: str) -> Optional[str]:
    """Get cached crawled content."""
    try:
        cache_key = f"crawl:{hashlib.md5(url.encode()).hexdigest()}"
        return redis_client.get(cache_key)
    except Exception:
        return None

def clear_cache_pattern(pattern: str = "llm_response:*"):
    """Clear cached responses matching pattern."""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass