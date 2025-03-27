# Constants and configuration for the SCP word extraction and definition lookup

import os

# API Configuration
DICTIONARY_API_KEY = os.environ.get("MERRIAM_WEBSTER_DICT_API_KEY")
THESAURUS_API_KEY = os.environ.get("MERRIAM_WEBSTER_THES_API_KEY")
DICTIONARY_API_BASE_URL = (
    "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
)
THESAURUS_API_BASE_URL = (
    "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/"
)

# Rate Limiting
DAILY_API_CALL_LIMIT = 1000
SAFE_CALL_LIMIT = 990  # Slightly under the limit to be safe

# Paths
DATA_DIR = "data"
DICTIONARY_DIR = os.path.join(DATA_DIR, "dictionary")
THESAURUS_DIR = os.path.join(DATA_DIR, "thesaurus")
SOURCE_DIR = "source"

# Word Processing
MIN_WORD_LENGTH = 2  # Minimum length to be considered a word
