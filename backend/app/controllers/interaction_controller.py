from fastapi import APIRouter, HTTPException
from app.models.interaction import InteractionModel
from app.services.openai_service import OpenAIService
from app.utils.database import get_database
from pydantic import BaseModel, Field
from typing import List, Optional
import os

router = APIRouter()

# Initialize services and database
db_client = get_database()
db = db_client["codegpt"]
openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models
class SubmitRequest(BaseModel):
    prompt: str = Field(..., description="The user's question or task.")
    code: Optional[str] = Field("", description="Code snippet provided by the user.")
    language: Optional[str] = Field("", description="Programming language context.")

class SubmitResponse(BaseModel):
    response: str = Field(..., description="The AI-generated response.")

@router.post(
    "/submit",
    response_model=SubmitResponse,
    summary="Submit a prompt to the AI model",
    description="Sends a prompt and optional code snippet to the AI model, returning a context-aware response."
)
async def submit_interaction(request: SubmitRequest):
    """
    Processes the user's input, generates a response using the AI model, and saves the interaction.
    """
    try:
        # Call the OpenAI service to generate a response
        response = openai_service.generate_response(request.prompt)

        # Save interaction to the database
        interaction = {
            "prompt": request.prompt,
            "response": response
        }
        db["interactions"].insert_one(interaction)

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class HistoryResponse(BaseModel):
    prompt: str
    response: str

@router.get(
    "/history",
    response_model=List[HistoryResponse],
    summary="Get interaction history",
    description="Retrieves the user's past interactions from the database."
)
async def get_interactions():
    """
    Fetches all past interactions from the database.
    """
    try:
        interactions = list(db["interactions"].find({}, {"_id": 0}))
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
