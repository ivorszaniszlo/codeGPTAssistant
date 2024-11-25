from pymongo import MongoClient
import os

def get_database() -> MongoClient:
    """
    Initializes and returns a MongoDB client based on the environment configuration.

    Returns:
        MongoClient: A client connected to the specified database.
    """
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    return client
