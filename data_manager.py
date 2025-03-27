# Functions for managing data storage and retrieval

import os
import json
import logging
import re
from constants import DICTIONARY_DIR, THESAURUS_DIR

logger = logging.getLogger("scp_extractor")


def ensure_data_directories():
    """Create necessary data directories if they don't exist."""
    os.makedirs(DICTIONARY_DIR, exist_ok=True)
    os.makedirs(THESAURUS_DIR, exist_ok=True)
    logger.info(f"Ensured data directories exist: {DICTIONARY_DIR}, {THESAURUS_DIR}")


def sanitize_filename(word):
    """
    Sanitize a word to be used as a filename.

    Args:
        word (str): The word to sanitize

    Returns:
        str: Sanitized filename-safe string
    """
    # Replace non-alphanumeric characters (except hyphen) with underscore
    return re.sub(r"[^a-zA-Z0-9\-]", "_", word)


def get_dictionary_path(word):
    """Get the path for a dictionary result file."""
    sanitized = sanitize_filename(word)
    return os.path.join(DICTIONARY_DIR, f"{sanitized}.json")


def get_thesaurus_path(word):
    """Get the path for a thesaurus result file."""
    sanitized = sanitize_filename(word)
    return os.path.join(THESAURUS_DIR, f"{sanitized}.json")


def dictionary_result_exists(word):
    """Check if dictionary result already exists for the word."""
    return os.path.exists(get_dictionary_path(word))


def thesaurus_result_exists(word):
    """Check if thesaurus result already exists for the word."""
    return os.path.exists(get_thesaurus_path(word))


def save_dictionary_result(word, data):
    """Save dictionary API result."""
    path = get_dictionary_path(word)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.debug(f"Saved dictionary result for '{word}'")


def save_thesaurus_result(word, data):
    """Save thesaurus result."""
    path = get_thesaurus_path(word)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.debug(f"Saved thesaurus result for '{word}'")


def load_source_fragments(fragment_paths):
    """
    Load and concatenate source fragments.

    Args:
        fragment_paths (list): List of paths to source fragments

    Returns:
        str: Concatenated content
    """
    content = ""
    for path in fragment_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                fragment_content = f.read()
                content += fragment_content + "\n"
                logger.debug(
                    f"Loaded fragment from {path} ({len(fragment_content)} characters)"
                )
        except Exception as e:
            logger.error(f"Failed to load fragment from {path}: {str(e)}")
            raise

    logger.info(
        f"Loaded {len(fragment_paths)} source fragments, total {len(content)} characters"
    )
    return content
