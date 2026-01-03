"""Configuration management for QA Engine."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings for the QA Engine."""

    # Base directories
    BASE_DIR = Path(__file__).parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    TEMP_DIR = BASE_DIR / "temp"
    DATA_DIR = BASE_DIR / "data"

    # Ensure directories exist
    TEMP_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    # File paths
    PARA_FILE = TEMP_DIR / "para.txt"
    IMP_INFO_FILE = TEMP_DIR / "imp_info.txt"
    IMP_SENTENCES_FILE = TEMP_DIR / "imp_sentences.txt"
    ABBR_DATA_FILE = DATA_DIR / "abbrtemp.txt"
    TRAINING_SET_FILE = DATA_DIR / "training_set5.txt"

    # API Configuration
    SEARCH_API_KEY: Optional[str] = os.getenv("SEARCH_API_KEY")
    SEARCH_ENGINE_ID: Optional[str] = os.getenv("SEARCH_ENGINE_ID")
    STANFORD_NER_URL: str = os.getenv(
        "STANFORD_NER_URL",
        "http://nlp.stanford.edu:8080/ner/"
    )

    # Processing parameters
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    TOP_PARAGRAPHS: int = int(os.getenv("TOP_PARAGRAPHS", "4"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # User Agent for web requests
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "qa_engine.log"

    @classmethod
    def cleanup_temp_files(cls) -> None:
        """Remove temporary files."""
        temp_files = [cls.PARA_FILE, cls.IMP_INFO_FILE, cls.IMP_SENTENCES_FILE]
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()

    @classmethod
    def get_temp_file_path(cls, filename: str) -> Path:
        """Get path for a temporary file."""
        return cls.TEMP_DIR / filename

    @classmethod
    def get_data_file_path(cls, filename: str) -> Path:
        """Get path for a data file."""
        return cls.DATA_DIR / filename


# Create a default config instance
config = Config()
