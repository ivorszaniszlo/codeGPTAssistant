from pydantic import BaseModel, Field
from typing import List, Optional
from app.utils.database import get_database

class InteractionModel(BaseModel):
    """
    Represents a user interaction consisting of a prompt and a response.
    """
    prompt: str = Field(..., description="The user's prompt or question.")
    response: str = Field(..., description="The AI-generated response.")
    user_id: Optional[str] = Field(None, description="The user ID, if available.")

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
        self.db = get_database()[db_name]
        self.collection = self.db["interactions"]

    def save_interaction(self, interaction: InteractionModel) -> None:
        """
        Save a user interaction to the database.

        Args:
            interaction (InteractionModel): The interaction data to store.
        """
        # Convert the Pydantic model to a dictionary and insert it into the database
        self.collection.insert_one(interaction.dict(exclude_unset=True))

    def get_interactions(self, user_id: Optional[str] = None) -> List[dict]:
        """
        Retrieve interactions from the database.

        Args:
            user_id (Optional[str]): The ID of the user whose interactions are to be retrieved.

        Returns:
            List[dict]: A list of interaction records.
        """
        # Build the query to filter by user_id, if provided
        query = {"user_id": user_id} if user_id else {}

        # Retrieve and return the interactions, excluding the MongoDB "_id" field
        return list(self.collection.find(query, {"_id": 0}))
