"""Query formulation and processing module."""
from typing import List
import nltk
from nltk.corpus import stopwords

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryProcessor:
    """Processes questions to extract meaningful query keywords."""

    def __init__(self):
        """Initialize the query processor."""
        try:
            self.stopwords = set(stopwords.words('english'))
        except LookupError:
            logger.warning("NLTK stopwords not found. Downloading...")
            nltk.download('stopwords', quiet=True)
            self.stopwords = set(stopwords.words('english'))

        # Translation table for removing punctuation
        self.punctuation_table = str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

    def clean(self, question: str) -> str:
        """
        Remove punctuation from the question.

        Args:
            question: Input question string

        Returns:
            Question with punctuation removed
        """
        return question.translate(self.punctuation_table)

    def remove_stopwords(self, question: str) -> List[str]:
        """
        Remove stopwords from the question.

        Args:
            question: Input question string

        Returns:
            List of meaningful words (non-stopwords)
        """
        try:
            tokens = nltk.word_tokenize(question)
        except LookupError:
            logger.warning("NLTK punkt tokenizer not found. Downloading...")
            nltk.download('punkt', quiet=True)
            tokens = nltk.word_tokenize(question)

        query = [token for token in tokens if token.lower() not in self.stopwords]
        logger.debug(f"Removed stopwords. Query tokens: {query}")
        return query

    def process_query(self, question: str) -> List[str]:
        """
        Process a question to extract query keywords.

        Args:
            question: Input question string

        Returns:
            List of query keywords
        """
        logger.info(f"Processing query: {question}")
        question = question.lower()
        question = self.clean(question)
        query = self.remove_stopwords(question)
        logger.info(f"Extracted {len(query)} query keywords")
        return query


def ret_query(question: str) -> List[str]:
    """
    Legacy function for backward compatibility.

    Args:
        question: Input question string

    Returns:
        List of query keywords
    """
    processor = QueryProcessor()
    return processor.process_query(question)
