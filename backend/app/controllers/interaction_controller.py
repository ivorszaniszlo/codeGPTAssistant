from fastapi import APIRouter, HTTPException
from app.services.openai_service import OpenAIService
from app.utils.database import get_database
from app.utils.redis import get_redis_client
from app.utils.elasticsearch import get_elasticsearch_client
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.redis_service import RedisService
import os
import logging

# Logging setup
logger = logging.getLogger("uvicorn.error")

router = APIRouter()

# Initialize services and databases
try:
    db_client = get_database()
    db = db_client["codegpt"]
    logger.info("Connected to MongoDB successfully.")
except Exception as db_error:
    logger.error(f"Failed to connect to MongoDB: {db_error}")
    raise

# Initialize Redis client
try:
    redis_service = RedisService(host="redis", port=6379)
    redis_client = redis_service.client
    logger.info("Redis client initialized successfully.")
except Exception as redis_error:
    logger.error(f"Failed to initialize Redis client: {redis_error}")
    redis_client = None

try:
    elastic_client = get_elasticsearch_client()
    logger.info("Connected to ElasticSearch successfully.")
except Exception as elastic_error:
    logger.error(f"Failed to connect to ElasticSearch: {elastic_error}")
    raise

try:
    openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
    logger.info("OpenAI Service initialized successfully.")
except Exception as openai_error:
    logger.error(f"Failed to initialize OpenAI Service: {openai_error}")
    raise


# Pydantic models
class SubmitRequest(BaseModel):
    prompt: str = Field(..., description="The user's question or task.")
    code: Optional[str] = Field("", description="Code snippet provided by the user.")
    language: Optional[str] = Field("", description="Programming language context.")


class SubmitResponse(BaseModel):
    response: str = Field(..., description="The AI-generated response.")


class HistoryResponse(BaseModel):
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
        cached_response = None
        if redis_client:
            cached_response = redis_client.get(request.prompt)
            if cached_response:
                logger.info("Cache hit: Returning cached response.")
                return SubmitResponse(response=cached_response)
        else:
            logger.warning("Redis is not available, skipping cache lookup.")

        # Generate response using OpenAI
        response = openai_service.generate_response(prompt=request.prompt)

        # Save to Redis
        if redis_client:
            redis_client.set(request.prompt, response, ex=3600)
            logger.info("Response cached in Redis.")

        # Save to MongoDB
        try:
            interaction = {"prompt": request.prompt, "response": response}
            db["interactions"].insert_one(interaction)
            logger.info("Interaction saved to database successfully.")
        except Exception as db_error:
            logger.error(f"Failed to save interaction to database: {db_error}")

        return SubmitResponse(response=response)
    except Exception as e:
        logger.error(f"Error in submit_interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get(
    "/history",
    response_model=List[HistoryResponse],
    summary="Get interaction history",
    description="Retrieves the user's past interactions, with relevance-based search if a query is provided."
)
async def get_interactions(query: Optional[str] = None) -> List[HistoryResponse]:
    """
    Endpoint to retrieve past interactions, optionally filtered by a relevance-based query.
    """
    try:
        if query and elastic_client:
            logger.info(f"Searching ElasticSearch for query: {query}")
            try:
                search_results = elastic_client.search(index="qa_pairs", query={"match": {"prompt": query}})
                interactions = [
                    {"prompt": hit["_source"]["prompt"], "response": hit["_source"]["response"]}
                    for hit in search_results["hits"]["hits"]
                ]
                logger.info(f"Retrieved {len(interactions)} interactions from ElasticSearch.")
            except Exception as es_error:
                logger.error(f"Error querying ElasticSearch: {es_error}")
                interactions = []
        else:
            if not elastic_client:
                logger.warning("ElasticSearch client is None, skipping search functionality.")
            logger.info("Fetching all interactions from MongoDB.")
            interactions = list(db["interactions"].find({}, {"_id": 0}))
            logger.info(f"Retrieved {len(interactions)} interactions from MongoDB.")

        if not interactions:
            logger.info("No interactions found.")
            return []

        return [HistoryResponse(**interaction) for interaction in interactions]
    except Exception as e:
        logger.error(f"Error in get_interactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")
    