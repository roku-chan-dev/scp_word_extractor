#!/usr/bin/env python3
# Main script for SCP word extraction and definition lookup

import sys
import time
import argparse
from log_config import setup_logging
from word_extractor import extract_unique_words_from_wikidot
from mw_api import APIManager
from data_manager import (
    ensure_data_directories,
    dictionary_result_exists,
    thesaurus_result_exists,
    save_dictionary_result,
    save_thesaurus_result,
    load_source_fragments,
)


def main():
    """Main function that orchestrates the extraction and API lookup process."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Extract words from SCP Wiki content and look up definitions"
    )
    parser.add_argument(
        "--source", nargs="+", required=True, help="Path(s) to source file fragments"
    )
    parser.add_argument(
        "--start-word", default=None, help="Optional word to start from (for resuming)"
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=None,
        help="Maximum number of words to process (for testing)",
    )
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()
    logger.info("Starting SCP word extraction and definition lookup")

    # Ensure data directories exist
    ensure_data_directories()

    # Load and concatenate source fragments
    content = load_source_fragments(args.source)

    # Extract unique words
    logger.info("Extracting unique words from source content")
    words = extract_unique_words_from_wikidot(content)
    logger.info(f"Extracted {len(words)} unique words")

    # Limit words if max_words is specified
    if args.max_words is not None:
        words = words[: args.max_words]
        logger.info(f"Limiting to {args.max_words} words for processing")

    # Initialize API manager
    try:
        api = APIManager()
    except ValueError as e:
        logger.error(f"API initialization failed: {str(e)}")
        sys.exit(1)

    # Find start index if resuming
    start_idx = 0
    if args.start_word:
        start_word = args.start_word.lower()
        try:
            start_idx = words.index(start_word)
            logger.info(f"Resuming from word '{start_word}' (index {start_idx})")
        except ValueError:
            logger.warning(
                f"Start word '{start_word}' not found in word list, starting from beginning"
            )

    # Process words
    success_count = 0
    error_count = 0
    skip_count = 0
    dict_calls = 0
    thes_calls = 0

    try:
        for idx, word in enumerate(words[start_idx:], start_idx):
            logger.info(f"Processing word {idx + 1}/{len(words)}: '{word}'")

            # Dictionary lookup
            dict_result = None
            if not dictionary_result_exists(word):
                dict_result = api.get_dictionary_entry(word)
                save_dictionary_result(word, dict_result)
                dict_calls += 1

                # Check for rate limit or critical errors
                if (
                    isinstance(dict_result, dict)
                    and dict_result.get("status_code") == 429
                ):
                    logger.error("Rate limit exceeded, stopping")
                    break
            else:
                logger.debug(f"Dictionary entry for '{word}' already exists, skipping")
                skip_count += 1

            # Thesaurus lookup
            thes_result = None
            if not thesaurus_result_exists(word):
                thes_result = api.get_thesaurus_entry(word)
                save_thesaurus_result(word, thes_result)
                thes_calls += 1

                # Check for rate limit or critical errors
                if (
                    isinstance(thes_result, dict)
                    and thes_result.get("status_code") == 429
                ):
                    logger.error("Rate limit exceeded, stopping")
                    break
            else:
                logger.debug(f"Thesaurus entry for '{word}' already exists, skipping")
                skip_count += 1

            # Update success and error counts based on results
            if dict_result is not None:
                if not isinstance(dict_result, dict) or not dict_result.get("error"):
                    success_count += 1
                else:
                    error_count += 1

            if thes_result is not None:
                if not isinstance(thes_result, dict) or not thes_result.get("error"):
                    success_count += 1
                else:
                    error_count += 1

            # Add a small delay between words to be nice to the API
            time.sleep(0.1)

        last_idx = idx
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        last_idx = idx - 1
        if last_idx >= 0 and last_idx + 1 < len(words):
            logger.info(f"To resume, run with: --start-word {words[last_idx + 1]}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        last_idx = idx - 1
        if last_idx >= 0 and last_idx + 1 < len(words):
            logger.info(f"To resume, run with: --start-word {words[last_idx + 1]}")
        raise

    # Report statistics
    api_stats = api.get_api_stats()
    logger.info("=== Processing Complete ===")
    logger.info(f"Total unique words: {len(words)}")
    logger.info(
        f"Words processed this session: {last_idx - start_idx + 1 if last_idx >= start_idx else 0}/{len(words)}"
    )
    logger.info(
        f"API calls made: {api_stats['call_count']} (Dictionary: {dict_calls}, Thesaurus: {thes_calls})"
    )
    logger.info(f"Remaining API calls: {api_stats['remaining_calls']}")
    logger.info(f"Success count: {success_count}")
    logger.info(f"Error count: {error_count}")
    logger.info(f"Skip count: {skip_count}")
    logger.info(f"Elapsed time: {api_stats['elapsed_time']:.2f} seconds")
    logger.info(f"Average rate: {api_stats['calls_per_minute']:.2f} calls per minute")

    if last_idx < len(words) - 1:
        logger.info(f"To resume, run with: --start-word {words[last_idx + 1]}")
    else:
        logger.info("All words processed successfully")


if __name__ == "__main__":
    main()
