from opensearchpy import OpenSearch, RequestsHttpConnection
from logging import Logger
from typing import Any

def get_opensearch_client(host: str, port: int) -> OpenSearch:
    """
    Initialize and return an OpenSearch client instance.
    """
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection
    )
    return client


def create_index_if_not_exists(client: OpenSearch, index_name: str, logger: Logger) -> None:
    """
    Create the OpenSearch index with a predefined schema if it doesn't exist.
    """
    if not client.indices.exists(index=index_name):
        logger.info(f"Index '{index_name}' does not exist. Creating it...")
        try:
            client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "Trace.StartTime": {"type": "date"},
                            "Trace.SourceType": {"type": "keyword"},
                            "Trace.Action": {"type": "keyword"},
                            "Trace.SessionId": {"type": "keyword"},
                            "Trace.Account": {"type": "keyword"},
                            "Trace.Type": {"type": "keyword"},
                            "Trace.Time": {"type": "float"},
                            "Trace.Id": {"type": "keyword"},
                            "Trace.Parent": {"type": "keyword"},
                            "Trace.TxId": {"type": "long"}
                        }
                    }
                },
            )
            logger.info(f"Index '{index_name}' created successfully.")
        except Exception as e:
            logger.info(f"Error creating index '{index_name}': {e}")
            exit(1)


def send_to_opensearch(client: OpenSearch, data: list[dict], logger: Logger) -> None:
    """
    Send a batch of log entries to OpenSearch using the bulk API.
    """
    if not data:
        return
    try:
        response = client.bulk(body=data)
        if response['errors']:
            logger.info("Errors occurred during bulk indexing:")
            for item in response['items']:
                if 'error' in item['index']:
                    logger.info(f"  Item error: {item['index']['error']}")
        else:
            logger.info(f"Successfully indexed {len(data) / 2} documents.")
        logger.debug(f"Bulk API response: {response}")
    except Exception as e:
        logger.info(f"Failed to send data to OpenSearch: {e}")
        logger.debug("Exception details:", exc_info=True)


def test_opensearch_connection(client: OpenSearch, logger: Logger) -> bool:
    """
    Test the connection to OpenSearch and log the result.
    Returns True if connection is successful, False otherwise.
    """
    try:
        info = client.info()
        logger.info(f"Successfully connected to OpenSearch: {info['version']['distribution']} {info['version']['number']}")
        logger.debug(f"OpenSearch connection info: {info}")
        return True
    except Exception as e:
        logger.info(f"Could not connect to OpenSearch. Please check configuration and network. Error: {e}")
        logger.debug("Exception details:", exc_info=True)
        return False 