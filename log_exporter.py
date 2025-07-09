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
import time


# --- Configuration ---
load_dotenv()

OPENSEARCH_HOST = os.getenv('OPENSEARCH_HOST')
OPENSEARCH_PORT = int(os.getenv('OPENSEARCH_PORT', 9200))
OPENSEARCH_INDEX = os.getenv('OPENSEARCH_INDEX')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH')
logger = get_logger(__name__)


def yield_log_lines(file_path: str):
    """
    Generator that yields each non-empty line from the log file.
    """
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


def parse_log_line(line: str) -> dict | None:
    """
    Parse a log line as JSON. Returns dict if successful, None otherwise.
    """
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        logger.info(f"Error decoding JSON in line: {line}")
        return None
    except Exception as e:
        logger.info(f"Unexpected error while parsing line: {line}. Error: {e}")
        return None


def add_to_bulk_data(bulk_data: list, log_entry: dict, index_name: str) -> None:
    """
    Add an OpenSearch bulk index action and the log entry to the bulk_data list.
    """
    bulk_data.append({
        "index": {
            "_index": index_name
        }
    })
    bulk_data.append(log_entry)


def export_log_to_opensearch(client, logger) -> None:
    '''
    Read the log file, parse lines, batch, and send entries to OpenSearch.
    '''
    bulk_data = []
    processed_lines = 0

    if not LOG_FILE_PATH:
        logger.info("Error: LOG_FILE_PATH environment variable is not set.")
        return

    try:
        if OPENSEARCH_INDEX is None:
            logger.info("Error: OPENSEARCH_INDEX environment variable is not set.")
            exit(1)
        for line in yield_log_lines(LOG_FILE_PATH):
            log_entry = parse_log_line(line)
            if log_entry is None:
                continue
            add_to_bulk_data(bulk_data, log_entry, OPENSEARCH_INDEX)
            processed_lines += 1
            if processed_lines % BATCH_SIZE == 0:
                logger.info(f"Processed {processed_lines} lines. Sending batch to OpenSearch...")
                send_to_opensearch(client, bulk_data, logger)
                bulk_data = []
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


def tail_log_lines(file_path: str, sleep_sec: float = 0.5):
    """
    Generator that yields new lines as they are appended to the file, starting at the end.
    """
    with open(file_path, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                yield line.rstrip('\n')
            else:
                time.sleep(sleep_sec)


def continuous_export_log_to_opensearch(
    client,
    logger,
    batch_size: int,
    flush_interval: float = 5.0,
    sleep_sec: float = 0.5
) -> None:
    """
    Continuously read new lines from a log file and export them to OpenSearch in batches.
    Flushes partial batches after flush_interval seconds.
    """
    bulk_data = []
    processed_lines = 0
    last_flush = time.time()

    if not LOG_FILE_PATH:
        logger.info("Error: LOG_FILE_PATH environment variable is not set.")
        return

    if OPENSEARCH_INDEX is None:
        logger.info("Error: OPENSEARCH_INDEX environment variable is not set.")
        exit(1)

    try:
        for line in tail_log_lines(LOG_FILE_PATH, sleep_sec=sleep_sec):
            log_entry = parse_log_line(line)
            if log_entry is None:
                continue
            add_to_bulk_data(bulk_data, log_entry, OPENSEARCH_INDEX)
            processed_lines += 1
            now = time.time()
            if processed_lines % batch_size == 0:
                logger.info(f"Processed {processed_lines} lines. Sending batch to OpenSearch...")
                send_to_opensearch(client, bulk_data, logger)
                bulk_data = []
                last_flush = now
            elif bulk_data and (now - last_flush) >= flush_interval:
                logger.info(f"Flush interval reached. Sending {len(bulk_data) // 2} lines to OpenSearch...")
                send_to_opensearch(client, bulk_data, logger)
                bulk_data = []
                last_flush = now
    except FileNotFoundError:
        logger.info(f"Error: Log file not found at {LOG_FILE_PATH}")
        return
    except Exception as e:
        logger.info(f"An error occurred while tailing or reading the log file: {e}")


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

    #export_log_to_opensearch(os_client, logger)
    continuous_export_log_to_opensearch(os_client, logger, BATCH_SIZE)
    logger.info("Log exporter finished.")