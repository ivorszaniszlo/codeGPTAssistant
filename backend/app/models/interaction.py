from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from app.utils.database import get_database
from app.utils.elasticsearch import get_elasticsearch_client
from app.services.redis_service import RedisService
from app.constants import (
    ELASTICSEARCH_INDEX_NAME,
    MONGODB_COLLECTION_NAME,
    CACHE_EXPIRATION_SECONDS
)
import logging
import os
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

# Environment variables
MONGO_URI = os.getenv("MONGODB_URI")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
ELASTICSEARCH_URI = os.getenv("ELASTICSEARCH_URI", "http://localhost:9200")


class InteractionModel(BaseModel):
    """
    Represents a user interaction consisting of a prompt and a response.
    """
    prompt: str = Field(..., description="The user's prompt or question.")
    response: str = Field(..., description="The AI-generated response.")
    user_id: Optional[str] = Field(None, description="The user ID, if available.")
    timestamp: Optional[str] = Field(None, description="Timestamp of the interaction.")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        if len(value) > 5000:
            raise ValueError("Prompt length exceeds 5000 characters.")
        return value


class InteractionDatabase:
    """
    Handles database interactions for storing and retrieving user prompts and responses.
    """
    def __init__(self):
        """
        Initializes the database connection and external services.
        """
        try:
            self.db_client = get_database(MONGO_URI)
            self.db = self.db_client[MONGODB_COLLECTION_NAME]
            self.collection = self.db["interactions"]

            # Initialize Elasticsearch
            self.elasticsearch = get_elasticsearch_client(ELASTICSEARCH_URI)

            # Initialize Redis
            self.redis_service = RedisService(host=REDIS_HOST, port=REDIS_PORT)
            self.redis = self.redis_service.client

            # Ensure indexes for efficient queries
            self.collection.create_index("user_id", sparse=True)
            self.collection.create_index("prompt")
            logger.info("Database and services initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize database or services: %s", str(e))
            raise RuntimeError("Database initialization failed.")

    def save_interaction(self, interaction: InteractionModel) -> None:
        """
        Save a user interaction to the database, Elasticsearch, and Redis.

        Args:
            interaction (InteractionModel): The interaction data to store.
        """
        try:
            # Save to MongoDB
            self.collection.insert_one(interaction.dict(exclude_unset=True))
            logger.info("Interaction saved to MongoDB successfully.")

            # Save to Elasticsearch
            if self.elasticsearch:
                self.elasticsearch.index(
                    index=ELASTICSEARCH_INDEX_NAME,
                    document=interaction.dict(exclude_unset=True),
                )
                logger.info("Interaction indexed in Elasticsearch successfully.")

            # Save to Redis
            if self.redis:
                redis_key = f"interaction:{interaction.prompt}"
                self.redis.set(redis_key, interaction.response, ex=CACHE_EXPIRATION_SECONDS)
                logger.info("Interaction cached in Redis successfully.")
        except Exception as e:
            logger.error("Failed to save interaction: %s", str(e))
            raise RuntimeError("Failed to save interaction.")

    def get_interactions(self, query: Optional[str] = None, user_id: Optional[str] = None) -> List[InteractionModel]:
        """
        Retrieve interactions from the database or Elasticsearch.

        Args:
            query (Optional[str]): Search query for similar prompts.
            user_id (Optional[str]): The ID of the user whose interactions are to be retrieved.

        Returns:
            List[InteractionModel]: A list of interaction records.
        """
        try:
            if query and self.elasticsearch:
                # Search in Elasticsearch
                search_results = self.elasticsearch.search(
                    index=ELASTICSEARCH_INDEX_NAME,
                    query={"match": {"prompt": query}},
                )
                interactions = [
                    InteractionModel(
                        prompt=hit["_source"]["prompt"],
                        response=hit["_source"]["response"]
                    )
                    for hit in search_results["hits"]["hits"]
                ]
                logger.info(f"Found {len(interactions)} interactions in Elasticsearch.")
                return interactions

            # Fallback to MongoDB
            query_filter = {"user_id": user_id} if user_id else {}
            records = list(self.collection.find(query_filter, {"_id": 0}))
            logger.info(f"Retrieved {len(records)} interactions from MongoDB.")
            return [InteractionModel(**record) for record in records]
        except InvalidId as e:
            logger.error("Invalid user ID provided: %s", str(e))
            raise ValueError("Invalid user ID format.")
        except Exception as e:
            logger.error("Failed to retrieve interactions: %s", str(e))
            raise RuntimeError("Failed to retrieve interactions.")
