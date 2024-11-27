import os

# ---------------------
# Application-wide constants
# ---------------------

# Redis cache expiration time in seconds
CACHE_EXPIRATION_SECONDS = int(os.getenv("CACHE_EXPIRATION_SECONDS", 3600))

# MongoDB configuration
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "interactions")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

# Elasticsearch configuration
ELASTICSEARCH_INDEX_NAME = os.getenv("ELASTICSEARCH_INDEX_NAME", "qa_pairs")
ELASTICSEARCH_URI = os.getenv("ELASTICSEARCH_URI", "http://172.18.0.2:9200")

# Logging configuration
LOGGING_FORMAT = os.getenv(
    "LOGGING_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGING_DATE_FORMAT = os.getenv("LOGGING_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

# OpenAI configuration
DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-default-api-key")

# ---------------------
# Constants Explanation
# ---------------------
# CACHE_EXPIRATION_SECONDS: Defines the default TTL for Redis cache entries.
# MONGODB_COLLECTION_NAME: MongoDB collection for storing interactions.
# ELASTICSEARCH_INDEX_NAME: Elasticsearch index for storing question-answer pairs.
# LOGGING_FORMAT: The format used across application logs.
# LOGGING_DATE_FORMAT: The date-time format for logs.
# DEFAULT_OPENAI_MODEL: Specifies the OpenAI model to use if none is explicitly defined.
