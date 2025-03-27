# SCP Word Extractor

A Python utility to extract unique English words from SCP Wiki Wikidot source,
look up their definitions and thesaurus entries using the Merriam-Webster API,
and save the results locally.

## Features

- Extracts unique words from Wikidot syntax (including text, CSS, comments,
  URLs, etc.)
- Looks up words in Merriam-Webster Dictionary and Thesaurus APIs
- Respects API rate limits (1000 calls per day across both APIs)
- Persists results to avoid redundant API calls
- Supports resuming interrupted processing
- Comprehensive logging

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/scp-word-extractor.git
   cd scp-word-extractor
   ```

2. Install dependencies:

   ```bash
   pip install requests
   ```

3. Set up your Merriam-Webster API key as an environment variable:

   ```bash
   # Linux/macOS
   export DICTIONARY_API_KEY=your-dictionary-api-key-here
   export THESAURUS_API_KEY=your-thesaurus-api-key-here

   # Windows Command Prompt
   set DICTIONARY_API_KEY=your-dictionary-api-key-here
   set THESAURUS_API_KEY=your-thesaurus-api-key-here

   # Windows PowerShell
   $env:DICTIONARY_API_KEY="your-dictionary-api-key-here"
   $env:THESAURUS_API_KEY="your-thesaurus-api-key-here"
   ```

## Usage

### Basic Usage

Process all words from source files:

```bash
python main.py --source path/to/scp_fragment1.txt path/to/scp_fragment2.txt
```

### Resuming from a Specific Word

If processing was interrupted, you can resume from a specific word:

```bash
python main.py --source path/to/scp_fragment1.txt path/to/scp_fragment2.txt --start-word example
```

### Testing with Limited Words

Process only a limited number of words (useful for testing):

```bash
python main.py --source path/to/scp_fragment1.txt --max-words 10
```

## Output

Results are stored in the following directory structure:

```plaintext
data/
├── dictionary/
│   └── word1.json
│   └── word2.json
│   └── ...
└── thesaurus/
    └── word1.json
    └── word2.json
    └── ...
```

Each JSON file contains the raw API response for the corresponding word.

## Logging

Logs are saved to the `logs/` directory with timestamps, showing:

- Words processed
- API calls made
- Success/error counts
- Rate limiting information
- Resume instructions if interrupted

## Project Structure

- `main.py`: Main script that orchestrates the extraction and API lookup process
- `constants.py`: Configuration settings and constants
- `log_config.py`: Logging configuration
- `word_extractor.py`: Functions for extracting words from Wikidot content
- `mw_api.py`: Merriam-Webster API interaction
- `data_manager.py`: Data storage and retrieval functions

## Error Handling

- Words not found in the APIs are stored with an error message
- Network errors are retried with exponential backoff
- Rate limit errors cause graceful termination with resume information
- Keyboard interruptions provide resume instructions

## Future Improvements

- Add filtering options for stop words or specific word patterns
- Implement a database backend for handling larger datasets
- Add analysis functions for the collected dictionary/thesaurus data
- Improve word extraction with a more sophisticated Wikidot parser

## License

MIT License
