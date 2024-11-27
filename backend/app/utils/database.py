import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Optional
import os

# Logging setup
logger = logging.getLogger("database")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class DatabaseService:
    """
    A service class to manage MongoDB connections.
    Implements the Singleton pattern to ensure a single MongoDB connection across the app.
    """
    _instance: Optional["DatabaseService"] = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation to ensure a single MongoDB connection instance.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self, uri: Optional[str] = None):
        """
        Initializes the MongoDB client.

        Args:
            uri (Optional[str]): The MongoDB connection URI. If None, uses the MONGODB_URI environment variable.
        """
        if not hasattr(self, "client"):  # Ensure initialization happens only once
            self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            self.client = None  # Initialize the client as None
            self._initialize_client()

    def _initialize_client(self):
        """
        Initializes the MongoDB client and tests the connection.
        """
        try:
            self.client = MongoClient(self.uri)
            # Test the connection
            self.client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB at {self.uri}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
            raise RuntimeError("MongoDB connection failed.")
        except OperationFailure as e:
            logger.error(f"Operation error in MongoDB: {e}", exc_info=True)
            raise RuntimeError("MongoDB operation failed.")

    def get_client(self) -> MongoClient:
        """
        Returns the MongoDB client.

        Returns:
            MongoClient: The MongoDB client instance.
        """
        if not self.client:
            logger.warning("MongoDB client was uninitialized. Reinitializing...")
            self._initialize_client()
        return self.client


# Singleton getter
def get_database() -> MongoClient:
    """
    Returns a singleton instance of the MongoDB client.

    Returns:
        MongoClient: The MongoDB client instance.
    """
    try:
        db_service = DatabaseService()
        return db_service.get_client()
    except RuntimeError as e:
        logger.error(f"Could not initialize MongoDB client: {e}")
        raise
