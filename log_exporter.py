import json
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from dotenv import load_dotenv


# --- Configuration ---
load_dotenv()

OPENSEARCH_HOST = os.getenv('OPENSEARCH_HOST')
OPENSEARCH_PORT = int(os.getenv('OPENSEARCH_PORT', 9200))
OPENSEARCH_INDEX = os.getenv('OPENSEARCH_INDEX')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH')


def get_opensearch_client():
    '''
    OpenSearch Client Initialization
    '''
    # For basic auth
    # client = OpenSearch(
    #     hosts = [{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    #     http_auth = ('your-username', 'your-password'),
    #     use_ssl = True,
    #     verify_certs = True,
    #     connection_class = RequestsHttpConnection
    # )

    # For anonymous/no authentication
    client = OpenSearch(
        hosts = [{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
        use_ssl = False,
        verify_certs = False,
        connection_class = RequestsHttpConnection
    )
    
    return client


def create_index_if_not_exists(client, index_name):
    """
    Creates the OpenSearch index with a predefined schema if it doesn't exist.
    """
    if not client.indices.exists(index=index_name):
        print(f"Index '{index_name}' does not exist. Creating it...")
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
            print(f"Index '{index_name}' created successfully.")
        except Exception as e:
            print(f"Error creating index '{index_name}': {e}")
            exit(1)


def process_log_file(client):
    '''
    Log Processing Function
    '''
    bulk_data = []
    processed_lines = 0

    if not LOG_FILE_PATH:
        print("Error: LOG_FILE_PATH environment variable is not set.")
        return

    try:
        with open(LOG_FILE_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)

                    bulk_data.append({
                        "index": {
                            "_index": OPENSEARCH_INDEX
                        }
                    })
                    bulk_data.append(log_entry)
                    processed_lines += 1

                    if processed_lines % BATCH_SIZE == 0:
                        print(f"Processed {processed_lines} lines. Sending batch to OpenSearch...")
                        send_to_opensearch(client, bulk_data)
                        bulk_data = []

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in line: {line}. Error: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while processing line: {line}. Error: {e}")

    except FileNotFoundError:
        print(f"Error: Log file not found at {LOG_FILE_PATH}")
        return
    except Exception as e:
        print(f"An error occurred while opening or reading the log file: {e}")
    finally:
        # Send any remaining data in the buffer before exiting
        if bulk_data:
            print(f"Sending remaining {len(bulk_data) / 2} lines to OpenSearch...")
            send_to_opensearch(client, bulk_data)


def send_to_opensearch(client, data):
    '''
    Send to OpenSearch Function
    '''
    if not data:
        return

    try:
        response = client.bulk(body=data)
        if response['errors']:
            print("Errors occurred during bulk indexing:")
            for item in response['items']:
                if 'error' in item['index']:
                    print(f"  Item error: {item['index']['error']}")
        else:
            print(f"Successfully indexed {len(data) / 2} documents.")
    except Exception as e:
        print(f"Failed to send data to OpenSearch: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting OpenSearch log exporter...")
    os_client = get_opensearch_client()

    # Verify OpenSearch connection
    try:
        info = os_client.info()
        print(f"Successfully connected to OpenSearch: {info['version']['distribution']} {info['version']['number']}")
    except Exception as e:
        print(f"Could not connect to OpenSearch. Please check configuration and network. Error: {e}")
        exit(1)

    create_index_if_not_exists(os_client, OPENSEARCH_INDEX)

    process_log_file(os_client)
    print("Log exporter finished.")