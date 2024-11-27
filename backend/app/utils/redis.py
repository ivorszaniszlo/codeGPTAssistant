import redis
import logging
import os
from typing import Optional

# Logger setup
logger = logging.getLogger("redis_client")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class RedisClient:
    """
    A singleton service to manage Redis connections.
    """
    _instance: Optional["RedisClient"] = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation to ensure a single Redis connection across the app.
        """
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None, db: int = 0, decode_responses: bool = True):
        """
        Initializes the Redis client.

        Args:
            host (Optional[str]): The Redis server host. Defaults to `REDIS_HOST` env variable or "localhost".
            port (Optional[int]): The Redis server port. Defaults to `REDIS_PORT` env variable or 6379.
            db (int): The Redis database index. Default is 0.
            decode_responses (bool): Whether to decode Redis responses to strings. Default is True.
        """
        if not hasattr(self, "client"):  # Ensure initialization happens only once
            self.host = host or os.getenv("REDIS_HOST", "localhost")
            self.port = port or int(os.getenv("REDIS_PORT", 6379))
            self.db = db
            self.decode_responses = decode_responses

            try:
                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=self.decode_responses
                )

                # Test the connection
                self.client.ping()
                logger.info(f"Connected to Redis at {self.host}:{self.port} successfully.")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis at {self.host}:{self.port}: {e}", exc_info=True)
                raise RuntimeError("Redis connection failed.")
            except Exception as e:
                logger.error(f"Unexpected error during Redis initialization: {e}", exc_info=True)
                raise RuntimeError("Unexpected error during Redis initialization.")

    def get_client(self) -> redis.Redis:
        """
        Returns the Redis client instance.

        Returns:
            redis.Redis: The Redis client.
        """
        return self.client


# Singleton getter
def get_redis_client() -> Optional[redis.Redis]:
    """
    Returns a singleton instance of the Redis client.

    Returns:
        Optional[redis.Redis]: The Redis client instance.
    """
    try:
        redis_service = RedisClient()
        return redis_service.get_client()
    except RuntimeError as e:
        logger.error(f"Could not initialize Redis client: {e}")
        return None

def redis_set_key(client, key: str, value: str) -> bool:
    try:
        client.set(key, value)
        return True
    except Exception as e:
        logger.error(f"Failed to set key {key} in Redis: {e}")
        return False


def redis_get_key(client, key: str) -> Optional[str]:
    try:
        return client.get(key)
    except Exception as e:
        logger.error(f"Failed to get key {key} from Redis: {e}")
        return None


def redis_delete_key(client, key: str) -> bool:
    try:
        return client.delete(key) > 0
    except Exception as e:
        logger.error(f"Failed to delete key {key} from Redis: {e}")
        return False
