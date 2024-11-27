from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.utils.database import get_database
from app.utils.elasticsearch import get_elasticsearch_client
from app.services.redis_service import RedisService
from app.services.openai_service import OpenAIService
from app.constants import MONGODB_COLLECTION_NAME
from app.controllers.interaction_controller import router as interaction_router
from dotenv import load_dotenv

import logging

# Logger setup
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for resource initialization and cleanup.
    """
    mongo_client = None
    elastic_client = None
    redis_client = None

    try:
        # MongoDB Initialization
        mongo_client = get_database()
        db = mongo_client[MONGODB_COLLECTION_NAME]
        logger.info("Connected to MongoDB successfully.")

        # Redis Initialization
        redis_service = RedisService()
        redis_client = redis_service.client
        logger.info("Connected to Redis successfully.")

        # Elasticsearch Initialization
        elastic_client = get_elasticsearch_client()
        if not elastic_client:
            raise RuntimeError("Failed to initialize Elasticsearch.")
        logger.info("Connected to Elasticsearch successfully.")

        # OpenAI Initialization
        openai_service = OpenAIService()
        logger.info("OpenAI Service initialized successfully.")

        # Pass resources to the app context
        app.state.db = db
        app.state.redis_client = redis_client
        app.state.elastic_client = elastic_client
        app.state.openai_service = openai_service

        logger.info("Application initialized successfully with all services.")
        yield

    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
        raise

    finally:
        # Cleanup resources
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB client closed.")
        if redis_client:
            redis_client.close()
            logger.info("Redis client closed.")
        if elastic_client:
            elastic_client.close()
            logger.info("Elasticsearch client closed.")


# Initialize FastAPI application with lifespan context manager
app = FastAPI(
    title="CodeGPT Assistant API",
    description=(
        "API for a VSCode extension that provides AI-driven coding assistance, "
        "integrated with LangChain, OpenAI, and other services."
    ),
    version="0.0.1",
    lifespan=lifespan,
)

# CORS middleware setup
origins = [
    "http://localhost",  # Local development
    "http://localhost:3000",  # Frontend on localhost
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(interaction_router)

# Health check endpoint
@app.get("/health", tags=["Utility"])
async def health_check():
    """
    Health check endpoint that verifies the status of connected services.
    """
    health_status = {
        "status": "healthy",
        "services": {
            "mongodb": "connected" if app.state.db else "disconnected",
            "redis": "connected" if app.state.redis_client else "disconnected",
            "elasticsearch": "connected" if app.state.elastic_client else "disconnected",
            "openai": "initialized" if app.state.openai_service else "uninitialized",
        },
    }
    return health_status
