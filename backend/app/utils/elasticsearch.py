from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, AuthenticationException, TransportError
from typing import Optional
import logging
import os

# Logger setup
logger = logging.getLogger("elasticsearch")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class ElasticsearchService:
    """
    A singleton service to manage Elasticsearch connections.
    """
    _instance: Optional["ElasticsearchService"] = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton implementation to ensure a single Elasticsearch connection.
        """
        if cls._instance is None:
            cls._instance = super(ElasticsearchService, cls).__new__(cls)
        return cls._instance

    def __init__(self, host: Optional[str] = None):
        """
        Initializes the Elasticsearch client.

        Args:
            host (Optional[str]): The Elasticsearch server URL. Defaults to `ELASTICSEARCH_URI` env variable.
        """
        if not hasattr(self, "client"):  # Ensure initialization happens only once
            self.host = host or os.getenv("ELASTICSEARCH_URI", "http://localhost:9200")
            try:
                self.client = Elasticsearch(hosts=[self.host])

                # Ping the server to verify the connection
                if not self.client.ping():
                    raise ConnectionError("Ping to Elasticsearch failed.")

                logger.info(f"Successfully connected to Elasticsearch at {self.host}")
            except ConnectionError as e:
                logger.error(f"Failed to connect to Elasticsearch: {e}", exc_info=True)
                raise RuntimeError("Elasticsearch connection failed.")
            except AuthenticationException as e:
                logger.error(f"Authentication failed for Elasticsearch: {e}", exc_info=True)
                raise RuntimeError("Elasticsearch authentication failed.")
            except TransportError as e:
                logger.error(f"Transport error while connecting to Elasticsearch: {e}", exc_info=True)
                raise RuntimeError("Elasticsearch transport error.")
            except Exception as e:
                logger.error(f"Unexpected error during Elasticsearch connection: {e}", exc_info=True)
                raise RuntimeError("Unexpected error during Elasticsearch initialization.")

    def get_client(self) -> Elasticsearch:
        """
        Returns the Elasticsearch client instance.

        Returns:
            Elasticsearch: The Elasticsearch client.
        """
        return self.client


# Singleton getter
def get_elasticsearch_client() -> Optional[Elasticsearch]:
    """
    Returns a singleton instance of the Elasticsearch client.

    Returns:
        Optional[Elasticsearch]: The Elasticsearch client instance.
    """
    try:
        es_service = ElasticsearchService()
        return es_service.client
    except RuntimeError as e:
        logger.error(f"Could not initialize Elasticsearch client: {e}")
        return None
