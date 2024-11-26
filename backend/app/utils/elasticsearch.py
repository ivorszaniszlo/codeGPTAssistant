from elasticsearch import Elasticsearch
from typing import Optional

def get_elasticsearch_client() -> Optional[Elasticsearch]:
    """
    Initialize and return an Elasticsearch client.

    This function creates a connection to the Elasticsearch server running at
    `http://localhost:9200`. If the connection fails, it logs the error and
    returns `None`.

    Returns:
        Optional[Elasticsearch]: An instance of the Elasticsearch client if the
                                 connection is successful, otherwise `None`.
    """
    try:
        # Define the Elasticsearch client
        client = Elasticsearch(hosts=["http://localhost:9200"])
        
        # Ping the server to check connectivity
        if not client.ping():
            raise Exception("Ping to Elasticsearch failed.")
        
        print("Connected to Elasticsearch successfully.")
        return client
    except Exception as e:
        print(f"Failed to connect to Elasticsearch: {e}")
        return None
