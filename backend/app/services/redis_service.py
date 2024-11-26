import redis
import logging
from typing import Optional, Any

# Logger setup
logger = logging.getLogger("redis_service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class RedisService:
    """
    A service class to interact with the Redis database.
    """

    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation to ensure a single Redis connection across the app.
        """
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, decode_responses: bool = True):
        """
        Initializes the Redis client.

        Args:
            host (str): The Redis server host. Default is "localhost".
            port (int): The Redis server port. Default is 6379.
            db (int): The Redis database index. Default is 0.
            decode_responses (bool): Whether to decode Redis responses to strings. Default is True.
        """
        if not hasattr(self, "client"):  # Ensure initialization happens only once
            try:
                self.client = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
                self.client.ping()  # Test the connection
                logger.info("Successfully connected to Redis.")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise RuntimeError("Redis initialization failed.")

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves the value for a given key from Redis.

        Args:
            key (str): The key to look up.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key does not exist.
        """
        try:
            value = self.client.get(key)
            logger.info(f"Retrieved value for key '{key}': {value}")
            return value
        except Exception as e:
            logger.error(f"Error retrieving key '{key}' from Redis: {e}")
            return None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Sets a value in Redis with an optional expiration time.

        Args:
            key (str): The key to set.
            value (Any): The value to store.
            ex (Optional[int]): Expiration time in seconds (optional).

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            self.client.set(key, value, ex=ex)
            logger.info(f"Set key '{key}' with value: {value} (expires in {ex} seconds)")
            return True
        except Exception as e:
            logger.error(f"Error setting key '{key}' in Redis: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Deletes a key from Redis.

        Args:
            key (str): The key to delete.

        Returns:
            bool: True if the key was deleted, False otherwise.
        """
        try:
            result = self.client.delete(key)
            if result:
                logger.info(f"Deleted key '{key}' from Redis.")
            else:
                logger.warning(f"Key '{key}' does not exist in Redis.")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting key '{key}' from Redis: {e}")
            return False

    def flush_db(self) -> bool:
        """
        Flushes the current Redis database.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            self.client.flushdb()
            logger.info("Redis database flushed successfully.")
            return True
        except Exception as e:
            logger.error(f"Error flushing Redis database: {e}")
            return False


# Singleton getter
def get_redis_service() -> RedisService:
    """
    Returns a singleton instance of RedisService.
    """
    try:
        return RedisService(host="redis", port=6379)  # Adjust host/port as per your setup
    except RuntimeError as e:
        logger.error(f"Could not initialize RedisService: {e}")
        raise
