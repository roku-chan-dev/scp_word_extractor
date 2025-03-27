# Functions for extracting words from Wikidot SCP content

import re
import logging
from constants import MIN_WORD_LENGTH

logger = logging.getLogger("scp_extractor")


def extract_unique_words_from_wikidot(content):
    """
    Extract a unique list of potential English words from Wikidot source content.

    Args:
        content (str): The Wikidot source content

    Returns:
        list: A sorted list of unique lowercase words
    """
    logger.info("Beginning word extraction from content")

    # Step 1: Handle CSS blocks separately
    # Extract words from CSS, then remove the blocks
    css_blocks = re.findall(
        r"\[\[module CSS\]\](.*?)\[\[\/module\]\]", content, re.DOTALL
    )
    css_words = []
    for css in css_blocks:
        css_words.extend(extract_words_from_css(css))

    # Remove CSS blocks from content
    content = re.sub(
        r"\[\[module CSS\]\](.*?)\[\[\/module\]\]", " ", content, flags=re.DOTALL
    )

    # Step 2: Handle other Wikidot syntax while preserving words

    # Replace [[...]] with spaces + content + spaces
    content = re.sub(r"\[\[(.*?)\]\]", lambda m: " " + m.group(1) + " ", content)

    # Replace formatting markers like **...**, //...// with spaces + content + spaces
    content = re.sub(
        r"(\*\*|\/{2}|__|--)(.*?)(\*\*|\/{2}|__|--)",
        lambda m: " " + m.group(2) + " ",
        content,
    )

    # Handle other syntax like {{...}}, @@...@@, etc.
    content = re.sub(
        r"(\{\{|\@\@)(.*?)(\}\}|\@\@)", lambda m: " " + m.group(2) + " ", content
    )

    # Step 3: Extract words from pre-processed content
    # This pattern looks for words with at least one letter
    # Allows words with apostrophes and hyphens like "don't" or "self-aware"
    word_pattern = r"[a-zA-Z][a-zA-Z\'\-]*[a-zA-Z\'\-]|[a-zA-Z]"
    raw_words = re.findall(word_pattern, content)

    # Step 4: Clean and filter words
    words = set()
    for word in raw_words + css_words:
        word = word.lower()  # Convert to lowercase
        # Filter by minimum length
        if len(word) >= MIN_WORD_LENGTH:
            words.add(word)

    result = sorted(words)
    logger.info(f"Extracted {len(result)} unique words")
    return result


def extract_words_from_css(css_content):
    """
    Extract words from CSS content.

    Args:
        css_content (str): CSS content block

    Returns:
        list: List of words extracted from CSS
    """
    words = []

    # Extract words from CSS comments
    comments = re.findall(r"\/\*(.*?)\*\/", css_content, re.DOTALL)
    for comment in comments:
        words.extend(re.findall(r"[a-zA-Z][a-zA-Z\'\-]*[a-zA-Z\'\-]|[a-zA-Z]", comment))

    # Remove comments to avoid duplication
    css_content = re.sub(r"\/\*(.*?)\*\/", " ", css_content, flags=re.DOTALL)

    # Extract CSS property names and values
    properties = re.findall(r"([a-zA-Z\-]+)\s*:\s*([^;]+);", css_content)
    for prop, value in properties:
        # Add property name
        words.extend(re.findall(r"[a-zA-Z][a-zA-Z\'\-]*[a-zA-Z\'\-]|[a-zA-Z]", prop))

        # Add property values - exclude hex colors and numeric values
        # Skip known color values and functions
        skip_values = ["rgb", "rgba", "hsl", "hsla", "url"]
        value_words = re.findall(r"[a-zA-Z][a-zA-Z\'\-]*[a-zA-Z\'\-]|[a-zA-Z]", value)
        for word in value_words:
            if word.lower() not in skip_values:
                words.append(word)

    # Extract words from selectors
    selectors = re.findall(r"([.#]?[a-zA-Z][a-zA-Z0-9\-_]*)", css_content)
    for selector in selectors:
        if selector.startswith(".") or selector.startswith("#"):
            selector = selector[1:]  # Remove . or # prefix

        # Split by dashes, underscores and camelCase
        parts = re.findall(r"[a-zA-Z][a-z]*", selector)
        words.extend(parts)

    return words
