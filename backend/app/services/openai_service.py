from langchain_openai import ChatOpenAI
from app.services.redis_service import RedisService
import logging
import os
from typing import Optional

# Setup logger
logger = logging.getLogger("openai_service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

class OpenAIService:
    """
    A service for interacting with OpenAI's chat models.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, redis_service: Optional[RedisService] = None):
        """
        Initializes the OpenAIService with the provided API key, chat model, and Redis service.

        Args:
            api_key (Optional[str]): The API key for OpenAI. If not provided, it will be loaded from the environment variable `OPENAI_API_KEY`.
            model (Optional[str]): The chat model name to use. Defaults to `gpt-4o-mini`.
            redis_service (Optional[RedisService]): An optional RedisService instance for caching responses.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OpenAI API key is not provided.")
            raise ValueError("OpenAI API key is required.")

        self.model = model or "gpt-4o-mini"
        self.llm = ChatOpenAI(api_key=self.api_key, model=self.model)
        self.redis_service = redis_service or self._initialize_redis()

        logger.info(f"OpenAIService initialized with model: {self.model}")

    @staticmethod
    def _initialize_redis() -> Optional[RedisService]:
        """
        Initializes the Redis service using environment variables.

        Returns:
            RedisService: The initialized Redis service, or None if initialization fails.
        """
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_service = RedisService(host=redis_host, port=redis_port)
            logger.info("RedisService initialized successfully.")
            return redis_service
        except Exception as e:
            logger.error(f"Failed to initialize RedisService: {e}")
            return None

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the AI model based on the provided prompt.

        Args:
            prompt (str): The input prompt for the AI model.

        Returns:
            str: The generated response.

        Raises:
            Exception: If an error occurs during the generation process.
        """
        try:
            logger.info(f"Generating response for prompt: {prompt}")

            # Check Redis cache
            if self.redis_service:
                cached_response = self.redis_service.get(prompt)
                if cached_response:
                    logger.info("Cache hit: Returning cached response.")
                    return cached_response
            else:
                logger.warning("RedisService is not initialized. Skipping cache check.")

            # Send the prompt to the chat model
            response = self.llm.invoke([{"role": "user", "content": prompt}])

            # Extract content from response
            if hasattr(response, "content"):
                message_content = response.content
            elif isinstance(response, list) and response:
                message_content = response[0].get("content", "")
            else:
                logger.error(f"Unexpected response format: {response}")
                raise ValueError("Unexpected response format received from ChatOpenAI.")

            logger.info("Response generated successfully.")

            # Cache the response in Redis
            if self.redis_service:
                self.redis_service.set(prompt, message_content, ex=3600)  # Cache for 1 hour
                logger.info("Response cached in Redis.")

            return message_content
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}", exc_info=True)
            raise RuntimeError(f"An error occurred while generating the response: {str(e)}")
