from langchain_openai import ChatOpenAI
import logging

# Setup logger
logger = logging.getLogger("openai_service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

class OpenAIService:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initializes the OpenAIService with the provided API key and chat model.

        Args:
            api_key (str): The API key for OpenAI.
            model (str): The chat model name to use (default is "gpt-4o-mini").
        """
        self.llm = ChatOpenAI(api_key=api_key, model=model)
        logger.info(f"OpenAIService initialized with model: {model}")

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
            # Send the prompt to the chat model
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            
            # Log the full response for debugging
            logger.debug(f"Raw response: {response}")
            
            # Handle structured response types
            if hasattr(response, "content"):
                message_content = response.content
                logger.info(f"Response generated: {message_content}")
                return message_content
            elif isinstance(response, list) and response:
                # Handle list of messages
                logger.info("Response is a list; processing the first message.")
                message_content = response[0].get("content", "")
                logger.info(f"Response generated: {message_content}")
                return message_content
            else:
                logger.error(f"Unexpected response format: {response}")
                raise Exception("Unexpected response format received from ChatOpenAI.")
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}", exc_info=True)
            raise Exception(f"An error occurred while generating the response: {str(e)}")
