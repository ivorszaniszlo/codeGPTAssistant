from elasticsearch import Elasticsearch
import logging
from typing import Optional, Any, Dict, List

# Logger setup
logger = logging.getLogger("elasticsearch_service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

class ElasticsearchService:
    """
    A service class to interact with Elasticsearch.
    """

    def __init__(self, host: str = "http://localhost:9200"):
        """
        Initializes the Elasticsearch client.

        Args:
            host (str): The Elasticsearch server URL. Default is "http://localhost:9200".
        """
        try:
            self.client = Elasticsearch(hosts=[host])
            # Ping the server to verify the connection
            if not self.client.ping():
                raise ConnectionError("Ping to Elasticsearch failed.")
            logger.info("Successfully connected to Elasticsearch.")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise RuntimeError("Elasticsearch initialization failed.")

    def index_document(self, index: str, document: Dict[str, Any], doc_id: Optional[str] = None) -> bool:
        """
        Indexes a document into Elasticsearch.

        Args:
            index (str): The name of the Elasticsearch index.
            document (Dict[str, Any]): The document to index.
            doc_id (Optional[str]): An optional document ID. If None, Elasticsearch will auto-generate it.

        Returns:
            bool: True if the document was indexed successfully, False otherwise.
        """
        try:
            response = self.client.index(index=index, id=doc_id, document=document)
            logger.info(f"Document indexed successfully: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to index document into {index}: {e}")
            return False

    def get_document(self, index: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a document from Elasticsearch by ID.

        Args:
            index (str): The name of the Elasticsearch index.
            doc_id (str): The ID of the document to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The document if found, None otherwise.
        """
        try:
            response = self.client.get(index=index, id=doc_id)
            logger.info(f"Document retrieved successfully: {response}")
            return response["_source"]
        except Exception as e:
            logger.error(f"Failed to retrieve document {doc_id} from index {index}: {e}")
            return None

    def search_documents(self, index: str, query: Dict[str, Any], size: int = 10) -> List[Dict[str, Any]]:
        """
        Searches for documents in an Elasticsearch index.

        Args:
            index (str): The name of the Elasticsearch index.
            query (Dict[str, Any]): The search query.
            size (int): The maximum number of results to return. Default is 10.

        Returns:
            List[Dict[str, Any]]: A list of matching documents.
        """
        try:
            response = self.client.search(index=index, query=query, size=size)
            logger.info(f"Search completed successfully with {len(response['hits']['hits'])} hits.")
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Failed to search documents in index {index}: {e}")
            return []

    def delete_document(self, index: str, doc_id: str) -> bool:
        """
        Deletes a document from Elasticsearch by ID.

        Args:
            index (str): The name of the Elasticsearch index.
            doc_id (str): The ID of the document to delete.

        Returns:
            bool: True if the document was deleted successfully, False otherwise.
        """
        try:
            response = self.client.delete(index=index, id=doc_id)
            logger.info(f"Document deleted successfully: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id} from index {index}: {e}")
            return False

    def create_index(self, index: str, mappings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Creates an Elasticsearch index with optional mappings.

        Args:
            index (str): The name of the Elasticsearch index to create.
            mappings (Optional[Dict[str, Any]]): The index mappings.

        Returns:
            bool: True if the index was created successfully, False otherwise.
        """
        try:
            if self.client.indices.exists(index=index):
                logger.info(f"Index {index} already exists.")
                return True

            response = self.client.indices.create(index=index, body={"mappings": mappings} if mappings else None)
            logger.info(f"Index {index} created successfully: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index {index}: {e}")
            return False

    def delete_index(self, index: str) -> bool:
        """
        Deletes an Elasticsearch index.

        Args:
            index (str): The name of the Elasticsearch index to delete.

        Returns:
            bool: True if the index was deleted successfully, False otherwise.
        """
        try:
            if not self.client.indices.exists(index=index):
                logger.warning(f"Index {index} does not exist.")
                return False

            response = self.client.indices.delete(index=index)
            logger.info(f"Index {index} deleted successfully: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index {index}: {e}")
            return False
