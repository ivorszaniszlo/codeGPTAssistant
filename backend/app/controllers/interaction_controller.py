from fastapi import APIRouter, HTTPException
from app.services.openai_service import OpenAIService
from app.utils.database import get_database
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import logging

# Logging setup
logger = logging.getLogger("uvicorn.error")

router = APIRouter()

# Initialize services and database
try:
    db_client = get_database()
    db = db_client["codegpt"]
    logger.info("Connected to MongoDB successfully.")
except Exception as db_error:
    logger.error(f"Failed to connect to MongoDB: {db_error}")
    raise

try:
    openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    logger.info("OpenAI Service initialized successfully.")
except Exception as openai_error:
    logger.error(f"Failed to initialize OpenAI Service: {openai_error}")
    raise


# Pydantic models
class SubmitRequest(BaseModel):
    """
    Model for incoming user request to the AI assistant.
    """
    prompt: str = Field(..., description="The user's question or task.")
    code: Optional[str] = Field("", description="Code snippet provided by the user.")
    language: Optional[str] = Field("", description="Programming language context.")


class SubmitResponse(BaseModel):
    """
    Model for the response returned by the AI assistant.
    """
    response: str = Field(..., description="The AI-generated response.")


class HistoryResponse(BaseModel):
    """
    Model for representing historical interactions.
    """
    prompt: str
    response: str


@router.post(
    "/submit",
    response_model=SubmitResponse,
    summary="Submit a prompt to the AI model",
    description="Sends a prompt and optional code snippet to the AI model, returning a context-aware response."
)
async def submit_interaction(request: SubmitRequest) -> SubmitResponse:
    """
    Endpoint to process user input and generate an AI response.
    """
    try:
        logger.info(f"Processing submit request with prompt: {request.prompt}")
        
        # Call the OpenAI service to generate a response
        response = openai_service.generate_response(prompt=request.prompt)

        # Save interaction to the database
        interaction = {"prompt": request.prompt, "response": response}
        db["interactions"].insert_one(interaction)
        logger.info("Interaction saved to database successfully.")

        return SubmitResponse(response=response)
    except Exception as e:
        logger.error(f"Error in submit_interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get(
    "/history",
    response_model=List[HistoryResponse],
    summary="Get interaction history",
    description="Retrieves the user's past interactions from the database."
)
async def get_interactions() -> List[HistoryResponse]:
    """
    Endpoint to retrieve all past interactions from the database.
    """
    try:
        logger.info("Fetching interaction history from the database.")
        interactions = list(db["interactions"].find({}, {"_id": 0}))
        logger.info(f"Retrieved {len(interactions)} interactions from the database.")
        return [HistoryResponse(**interaction) for interaction in interactions]
    except Exception as e:
        logger.error(f"Error in get_interactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")
