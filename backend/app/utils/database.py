import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import os

# Logging setup
logger = logging.getLogger("database")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

def get_database() -> MongoClient:
    """
    Initializes and returns a MongoDB client based on the environment configuration.

    Returns:
        MongoClient: A client connected to the specified database.
    Raises:
        RuntimeError: If the connection to MongoDB fails.
    """
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    try:
        client = MongoClient(uri)
        # Check if the connection works
        client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
        return client
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise RuntimeError(f"Failed to connect to MongoDB: {e}")
    except OperationFailure as e:
        logger.error(f"Operation error in MongoDB: {e}", exc_info=True)
        raise RuntimeError(f"Operation error in MongoDB: {e}")
    