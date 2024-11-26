import redis
import logging
from typing import Optional

# Logger setup
logger = logging.getLogger("redis_client")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

def get_redis_client() -> Optional[redis.Redis]:
    """
    Initialize and return a Redis client.

    This function creates a connection to the Redis server running at
    `localhost` on port `6379`. If the connection fails, it logs the error and
    returns `None`.

    Returns:
        Optional[redis.Redis]: An instance of the Redis client if the connection
                               is successful, otherwise `None`.
    """
    try:
        # Define the Redis client with response decoding enabled
        client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        
        # Ping the Redis server to check connectivity
        client.ping()
        logger.info("Connected to Redis successfully.")
        return client
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None
