import pytest
from unittest.mock import patch, MagicMock
from app.services.elasticsearch_service import ElasticsearchService


@pytest.fixture
def mock_elasticsearch_client():
    """
    Mock the Elasticsearch Python client.
    """
    with patch("app.services.elasticsearch_service.Elasticsearch") as MockElasticsearch:
        mock_client = MagicMock()
        MockElasticsearch.return_value = mock_client
        yield mock_client

def test_create_index_failure(mock_elasticsearch_client):
    """
    Test ElasticsearchService.create_index failure scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.indices.exists.return_value = False
    mock_elasticsearch_client.indices.create.side_effect = Exception("Creation failed")

    index_name = "test-index"
    mappings = {"properties": {"field": {"type": "text"}}}

    try:
        service.create_index(index_name, mappings)
    except Exception as e:
        print("DEBUG: Exception caught in test:", str(e))  # Debug
        assert str(e) == "Creation failed"  # Ensure the exception matches
    else:
        pytest.fail("Expected exception was not raised.")


def test_index_document_failure(mock_elasticsearch_client):
    """
    Test ElasticsearchService.index_document failure scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.index.side_effect = Exception("Indexing failed")

    index_name = "test-index"
    document = {"field": "value"}

    service.index_document(index_name, document)


def test_get_document_not_found(mock_elasticsearch_client):
    """
    Test ElasticsearchService.get_document when the document is not found.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.get.side_effect = Exception("Document not found")

    index_name = "test-index"
    doc_id = "nonexistent-id"

    service.get_document(index_name, doc_id)


def test_delete_index_failure(mock_elasticsearch_client):
    """
    Test ElasticsearchService.delete_index failure scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.indices.delete.side_effect = Exception("Deletion failed")

    index_name = "nonexistent-index"

    service.delete_index(index_name)


def test_create_index_success(mock_elasticsearch_client):
    """
    Test ElasticsearchService.create_index success scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.indices.exists.return_value = False
    mock_elasticsearch_client.indices.create.return_value = {"acknowledged": True}

    index_name = "test-index"
    mappings = {"properties": {"field": {"type": "text"}}}

    result = service.create_index(index_name, mappings)
    assert result is True
    mock_elasticsearch_client.indices.create.assert_called_once_with(index=index_name, body={"mappings": mappings})


def test_create_index_already_exists(mock_elasticsearch_client):
    """
    Test ElasticsearchService.create_index when the index already exists.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.indices.exists.return_value = True

    index_name = "test-index"
    mappings = {"properties": {"field": {"type": "text"}}}

    result = service.create_index(index_name, mappings)
    assert result is False
    mock_elasticsearch_client.indices.create.assert_not_called()


def test_index_document_success(mock_elasticsearch_client):
    """
    Test ElasticsearchService.index_document success scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.index.return_value = {"result": "created"}

    index_name = "test-index"
    document = {"field": "value"}

    result = service.index_document(index_name, document)
    assert result is True
    mock_elasticsearch_client.index.assert_called_once_with(
        index=index_name, document=document, id=None  # Include id=None explicitly
    )


def test_get_document_success(mock_elasticsearch_client):
    """
    Test ElasticsearchService.get_document success scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.get.return_value = {"_source": {"field": "value"}}

    index_name = "test-index"
    doc_id = "123"

    result = service.get_document(index_name, doc_id)
    assert result == {"field": "value"}
    mock_elasticsearch_client.get.assert_called_once_with(index=index_name, id=doc_id)


def test_search_documents_success(mock_elasticsearch_client):
    """
    Test ElasticsearchService.search_documents success scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.search.return_value = {
        "hits": {"hits": [{"_source": {"field": "value1"}}, {"_source": {"field": "value2"}}]}
    }

    index_name = "test-index"
    query = {"match": {"field": "value"}}

    result = service.search_documents(index_name, query)
    assert result == [{"field": "value1"}, {"field": "value2"}]
    mock_elasticsearch_client.search.assert_called_once_with(
        index=index_name, query=query, size=10  # Adjusted to match the actual API call
    )


def test_delete_document_success(mock_elasticsearch_client):
    """
    Test ElasticsearchService.delete_document success scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.delete.return_value = {"result": "deleted"}

    index_name = "test-index"
    doc_id = "123"

    result = service.delete_document(index_name, doc_id)
    assert result is True
    mock_elasticsearch_client.delete.assert_called_once_with(index=index_name, id=doc_id)


def test_delete_document_not_found(mock_elasticsearch_client):
    """
    Test ElasticsearchService.delete_document when the document is not found.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.delete.return_value = {"result": "not_found"}

    index_name = "test-index"
    doc_id = "nonexistent-id"

    result = service.delete_document(index_name, doc_id)
    assert result is False
    mock_elasticsearch_client.delete.assert_called_once_with(index=index_name, id=doc_id)


def test_delete_index_success(mock_elasticsearch_client):
    """
    Test ElasticsearchService.delete_index success scenario.
    """
    service = ElasticsearchService()
    mock_elasticsearch_client.indices.delete.return_value = {"acknowledged": True}

    index_name = "test-index"

    result = service.delete_index(index_name)
    assert result is True
    mock_elasticsearch_client.indices.delete.assert_called_once_with(index=index_name)
