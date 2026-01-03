# Question-Answering Engine

A Python-based question-answering system that automatically answers factual questions by retrieving information from web sources, processing it, and extracting relevant answers using Natural Language Processing and Named Entity Recognition.

## Features

- **Question Classification**: Automatically classifies questions into types (WHO, WHERE, WHEN, WHAT, Abbreviations)
- **Web Information Retrieval**: Fetches relevant information from Google search results
- **Query Processing**: Extracts meaningful keywords from questions
- **Intelligent Scoring**: Ranks paragraphs and sentences by relevance
- **Named Entity Recognition**: Extracts specific entities (people, locations, dates) from text
- **Abbreviation Expansion**: Looks up and expands common abbreviations

## What's New in v2.0

✅ **Python 3 Compatible** - Migrated from Python 2.7 to Python 3.8+
✅ **Modern Dependencies** - Replaced deprecated libraries (urllib2 → requests, mechanize → requests)
✅ **Cross-Platform Paths** - No more hardcoded Windows paths
✅ **Proper Project Structure** - Organized into logical modules
✅ **Configuration Management** - Centralized config with environment variable support
✅ **Logging System** - Comprehensive logging for debugging
✅ **Type Hints** - Added type annotations for better code clarity
✅ **Unit Tests** - Test coverage for core components
✅ **Error Handling** - Robust error handling throughout

## Sample Queries

1. Who's the president of India?
2. Where did Sachin Tendulkar score his first test century?
3. When did the first person land on the moon?
4. What is the full form of NASA?

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Install

```bash
# Install dependencies
pip install -r requirements.txt

# Download NLTK data (required)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Usage

### Interactive Mode

```bash
python -m src.main
```

### Single Question

```bash
python -m src.main -q "Who is the president of India?"
```

### Batch Mode

```bash
python -m src.main -f questions.txt
```

## Project Structure

```
Question-Answering-Engine/
├── src/
│   ├── main.py                          # Main entry point
│   ├── classifiers/
│   │   └── question_classifier.py       # Question classification
│   ├── retrieval/
│   │   └── information_retriever.py     # Web search
│   ├── processing/
│   │   ├── query_processor.py           # Query formulation
│   │   ├── paragraph_scorer.py          # Paragraph scoring
│   │   ├── sentence_scorer.py           # Sentence scoring
│   │   ├── answer_extractor.py          # Answer extraction
│   │   └── abbreviation_expander.py     # Abbreviations
│   └── utils/
│       ├── config.py                    # Configuration
│       └── logger.py                    # Logging
├── tests/                               # Unit tests
├── data/                                # Data files
├── temp/                                # Temporary files
└── requirements.txt                     # Dependencies
```

## QA Pipeline Components

1. **Question Classification** - Determines expected answer type
2. **Information Retrieval** - Fetches web search results
3. **Query Reformulation** - Extracts keywords
4. **Paragraph Scoring** - Ranks paragraphs by relevance
5. **Sentence Scoring** - Ranks sentences with NER
6. **Answer Processing** - Extracts final answer

## Development

### Running Tests

```bash
pytest
pytest --cov=src
```

### Code Quality

```bash
black src/ tests/
flake8 src/ tests/
```

## Configuration

Copy `.env.example` to `.env` for custom settings:

```bash
MAX_SEARCH_RESULTS=10
TOP_PARAGRAPHS=4
LOG_LEVEL=INFO
```

## Legacy Code Note

The original Python 2.7 code is preserved in the root directory. The new Python 3 code is in the `src/` directory.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## License

MIT License
