import logging
import os
import json
from datetime import datetime
from typing import Optional

class JsonFormatter(logging.Formatter):
    """
    Logging formatter that outputs log records as JSON objects.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName,
            'lineNo': record.lineno,
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a logger configured with the JSON formatter and log level from LOG_LEVEL env var (default INFO).
    Ensures no duplicate handlers are added.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(log_level)
    logger.propagate = False
    return logger 