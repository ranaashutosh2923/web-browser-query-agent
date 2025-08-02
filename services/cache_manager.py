"""
Cache Manager Service
Manages Redis cache for storing and retrieving query results
"""

import redis
import json
import logging
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )

            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        import hashlib
        return f"query_result:{hashlib.md5(query.lower().encode()).hexdigest()}"

    def get_cached_result(self, query: str) -> dict:
        """
        Get cached result for a query

        Args:
            query (str): The query to search for

        Returns:
            dict: Cached result or None
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(query)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                result = json.loads(cached_data)
                logger.info(f"Cache hit for query: {query}")
                return result
            else:
                logger.info(f"Cache miss for query: {query}")
                return None

        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None

    def cache_result(self, query: str, result: dict, expiry_hours: int = 24) -> bool:
        """
        Cache a query result

        Args:
            query (str): The original query
            result (dict): The result to cache
            expiry_hours (int): Cache expiry in hours

        Returns:
            bool: Success status
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(query)

            # Add metadata
            cache_data = {
                "query": query,
                "result": result,
                "cached_at": datetime.now().isoformat(),
                "cache_key": cache_key
            }

            # Cache with expiry
            expiry_seconds = expiry_hours * 3600
            success = self.redis_client.setex(
                cache_key,
                expiry_seconds,
                json.dumps(cache_data, ensure_ascii=False)
            )

            if success:
                logger.info(f"Result cached for query: {query}")
                return True
            else:
                logger.error(f"Failed to cache result for query: {query}")
                return False

        except Exception as e:
            logger.error(f"Error caching result: {e}")
            return False

    def get_similar_cached_results(self, similar_queries: list) -> dict:
        """
        Get cached results for similar queries

        Args:
            similar_queries (list): List of similar query objects

        Returns:
            dict: Best cached result or None
        """
        if not self.redis_client or not similar_queries:
            return None

        # Try to get cached result for the most similar query
        for query_obj in similar_queries:
            cached_result = self.get_cached_result(query_obj['query'])
            if cached_result:
                logger.info(f"Found cached result for similar query: {query_obj['query']}")
                return cached_result

        return None

    def clear_cache(self) -> bool:
        """Clear all cached results"""
        if not self.redis_client:
            return False

        try:
            # Get all query result keys
            keys = self.redis_client.keys("query_result:*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached results")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {"error": "Redis not connected"}

        try:
            keys = self.redis_client.keys("query_result:*")
            return {
                "total_cached_queries": len(keys),
                "redis_info": self.redis_client.info(),
                "memory_usage": self.redis_client.memory_usage("query_result:*") if keys else 0
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
