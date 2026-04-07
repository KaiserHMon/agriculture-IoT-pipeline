import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def setup_logger(name="agriculture_iot", log_dir="logs"):
    """
    Configures a JSON logger for both console and a rotating file.
    This is ideal for CloudWatch and automated log aggregation.
    """
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # JSON Formatter
    # We include timestamp, level, name, and message as standard
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    log_filename = os.path.join(log_dir, f"{name}.jsonl")
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Global instance for easy access
logger = setup_logger()
