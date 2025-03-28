# Merriam-Webster API interaction

import json
import logging
import time
from urllib.parse import quote

import requests

from constants import (
    DICTIONARY_API_BASE_URL,
    DICTIONARY_API_KEY,
    SAFE_CALL_LIMIT,
    THESAURUS_API_BASE_URL,
    THESAURUS_API_KEY,
)

logger = logging.getLogger("scp_word_extractor")


class APIManager:
    """Manages interactions with Merriam-Webster APIs, including rate limiting."""

    def __init__(self):
        """Initialize the API manager with call tracking."""
        if not DICTIONARY_API_KEY or not THESAURUS_API_KEY:
            raise ValueError(
                "API keys not set. Please set MERRIAM_WEBSTER_DICT_API_KEY and MERRIAM_WEBSTER_THES_API_KEY."
            )

        self.dict_api_key = DICTIONARY_API_KEY
        self.thes_api_key = THESAURUS_API_KEY
        self.call_count = 0
        self.start_time = time.time()
        logger.info("API Manager initialized")

    def _make_request(self, url, max_retries=3, backoff_factor=1.5):
        """
        Make an API request with retries and backoff.

        Args:
            url (str): Full URL including API key
            max_retries (int): Maximum number of retry attempts
            backoff_factor (float): Factor for exponential backoff

        Returns:
            dict or list or None: JSON response data or error information
        """

        retries = 0
        while retries <= max_retries:
            try:
                logger.debug(f"Making API request (attempt {retries + 1})")
                response = requests.get(url, timeout=10)
                self.call_count += 1

                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {str(e)}")
                        return {"error": "JSON parse error", "status_code": -2}

                if response.status_code == 404:
                    # Word not found
                    logger.info("Word not found in API (404)")
                    return {"error": "Not Found", "status_code": 404}

                if response.status_code == 429:
                    # Rate limit exceeded
                    logger.error("API rate limit exceeded (429)")
                    return {"error": "Rate limit exceeded", "status_code": 429}

                # Handle other error codes
                logger.warning(
                    f"API request failed with status code {response.status_code}"
                )
                retries += 1
                if retries <= max_retries:
                    sleep_time = backoff_factor**retries
                    logger.info(
                        f"Retrying in {sleep_time:.2f} seconds (attempt {retries}/{max_retries})"
                    )
                    time.sleep(sleep_time)

            except requests.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                retries += 1
                if retries <= max_retries:
                    sleep_time = backoff_factor**retries
                    logger.info(
                        f"Retrying in {sleep_time:.2f} seconds (attempt {retries}/{max_retries})"
                    )
                    time.sleep(sleep_time)
                else:
                    return {"error": str(e), "status_code": -1}

        return {"error": "Max retries exceeded", "status_code": -1}

    def get_dictionary_entry(self, word):
        """
        Get dictionary entry for a word.

        Args:
            word (str): Word to look up

        Returns:
            dict or list: API response or error data
        """
        encoded_word = quote(word.lower())
        url = f"{DICTIONARY_API_BASE_URL}{encoded_word}?key={self.dict_api_key}"

        logger.info(f"Looking up dictionary entry for '{word}'")
        result = self._make_request(url)

        # Check if the result is a list of suggestions rather than definitions
        if (
            isinstance(result, list)
            and result
            and all(isinstance(item, str) for item in result)
        ):
            logger.info(f"No exact match for '{word}' in dictionary, got suggestions")
            return {
                "error": "Not Found (suggestions available)",
                "status_code": 404,
                "suggestions": result,
            }

        return result

    def get_thesaurus_entry(self, word):
        """
        Get thesaurus entry for a word.

        Args:
            word (str): Word to look up

        Returns:
            dict or list: API response or error data
        """
        encoded_word = quote(word.lower())
        url = f"{THESAURUS_API_BASE_URL}{encoded_word}?key={self.thes_api_key}"

        logger.info(f"Looking up thesaurus entry for '{word}'")
        result = self._make_request(url)

        # Check if the result is a list of suggestions rather than entries
        if (
            isinstance(result, list)
            and result
            and all(isinstance(item, str) for item in result)
        ):
            logger.info(f"No exact match for '{word}' in thesaurus, got suggestions")
            return {
                "error": "Not Found (suggestions available)",
                "status_code": 404,
                "suggestions": result,
            }

        return result

    def get_api_stats(self):
        """Get statistics about API usage in the current session."""
        elapsed_time = time.time() - self.start_time
        return {
            "call_count": self.call_count,
            "remaining_calls": SAFE_CALL_LIMIT - self.call_count,
            "elapsed_time": elapsed_time,
            "calls_per_minute": (
                (self.call_count / elapsed_time) * 60 if elapsed_time > 0 else 0
            ),
        }
