from pydantic import BaseModel, Field, validator
from typing import List, Optional
from app.utils.database import get_database
from bson.errors import InvalidId
import logging

logger = logging.getLogger(__name__)

class InteractionModel(BaseModel):
    """
    Represents a user interaction consisting of a prompt and a response.
    """
    prompt: str = Field(..., description="The user's prompt or question.")
    response: str = Field(..., description="The AI-generated response.")
    user_id: Optional[str] = Field(None, description="The user ID, if available.")

    @validator("prompt")
    def validate_prompt(cls, value):
        if len(value) > 5000:
            raise ValueError("Prompt length exceeds 5000 characters.")
        return value

class InteractionDatabase:
    """
    Handles database interactions for storing and retrieving user prompts and responses.
    """
    def __init__(self, uri: str, db_name: str = "codegpt"):
        """
        Initializes the database connection.

        Args:
            uri (str): The MongoDB connection URI.
            db_name (str): The name of the database to connect to.
        """
        try:
            self.db = get_database()[db_name]
            self.collection = self.db["interactions"]

            # Ensure the user_id field has an index for faster queries
            self.collection.create_index("user_id", sparse=True)
        except Exception as e:
            logger.error("Failed to initialize database: %s", str(e))
            raise RuntimeError("Database initialization failed.")

    def save_interaction(self, interaction: InteractionModel) -> None:
        """
        Save a user interaction to the database.

        Args:
            interaction (InteractionModel): The interaction data to store.
        """
        try:
            self.collection.insert_one(interaction.dict(exclude_unset=True))
        except Exception as e:
            logger.error("Failed to save interaction: %s", str(e))
            raise RuntimeError("Failed to save interaction.")

    def get_interactions(self, user_id: Optional[str] = None) -> List[InteractionModel]:
        """
        Retrieve interactions from the database.

        Args:
            user_id (Optional[str]): The ID of the user whose interactions are to be retrieved.

        Returns:
            List[InteractionModel]: A list of interaction records.
        """
        try:
            query = {"user_id": user_id} if user_id else {}
            records = list(self.collection.find(query, {"_id": 0}))

            return [InteractionModel(**record) for record in records]
        except InvalidId as e:
            logger.error("Invalid user ID provided: %s", str(e))
            raise ValueError("Invalid user ID format.")
        except Exception as e:
            logger.error("Failed to retrieve interactions: %s", str(e))
            raise RuntimeError("Failed to retrieve interactions.")
