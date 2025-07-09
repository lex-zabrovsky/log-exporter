import json
import os
from dotenv import load_dotenv
from logging_config import get_logger
from opensearch_utils import (
    get_opensearch_client,
    create_index_if_not_exists,
    send_to_opensearch,
    test_opensearch_connection
)


# --- Configuration ---
load_dotenv()

OPENSEARCH_HOST = os.getenv('OPENSEARCH_HOST')
OPENSEARCH_PORT = int(os.getenv('OPENSEARCH_PORT', 9200))
OPENSEARCH_INDEX = os.getenv('OPENSEARCH_INDEX')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH')
logger = get_logger(__name__)


def export_log_to_opensearch(client, logger) -> None:
    '''
    Process the log file and send entries to OpenSearch in batches.
    '''
    bulk_data = []
    processed_lines = 0

    if not LOG_FILE_PATH:
        logger.info("Error: LOG_FILE_PATH environment variable is not set.")
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
                        logger.info(f"Processed {processed_lines} lines. Sending batch to OpenSearch...")
                        send_to_opensearch(client, bulk_data, logger)
                        bulk_data = []

                except json.JSONDecodeError as e:
                    logger.info(f"Error decoding JSON in line: {line}. Error: {e}")
                except Exception as e:
                    logger.info(f"An unexpected error occurred while processing line: {line}. Error: {e}")

    except FileNotFoundError:
        logger.info(f"Error: Log file not found at {LOG_FILE_PATH}")
        return
    except Exception as e:
        logger.info(f"An error occurred while opening or reading the log file: {e}")
    finally:
        # Send any remaining data in the buffer before exiting
        if bulk_data:
            logger.info(f"Sending remaining {len(bulk_data) / 2} lines to OpenSearch...")
            send_to_opensearch(client, bulk_data, logger)


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Starting OpenSearch log exporter...")
    if OPENSEARCH_HOST is None:
        logger.info("Error: OPENSEARCH_HOST environment variable is not set.")
        exit(1)
    os_client = get_opensearch_client(OPENSEARCH_HOST, OPENSEARCH_PORT)

    if not test_opensearch_connection(os_client, logger):
        exit(1)

    if OPENSEARCH_INDEX is None:
        logger.info("Error: OPENSEARCH_INDEX environment variable is not set.")
        exit(1)
    create_index_if_not_exists(os_client, OPENSEARCH_INDEX, logger)

    export_log_to_opensearch(os_client, logger)
    logger.info("Log exporter finished.")