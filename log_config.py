# Logging configuration

import logging
import os
from datetime import datetime


def setup_logging():
    """Configure logging for the application."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_filename = f"scp_extractor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(log_dir, log_filename)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),  # Also log to console
        ],
    )

    # Create logger
    logger = logging.getLogger("scp_word_extractor")
    logger.info("Logging initialized")

    return logger
