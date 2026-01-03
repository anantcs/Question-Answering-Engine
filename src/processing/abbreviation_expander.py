"""Abbreviation expansion module."""
import re
from typing import Optional
from pathlib import Path

from ..utils.config import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class AbbreviationExpander:
    """Expands abbreviations using a lookup dictionary."""

    def __init__(self, abbr_file: Optional[Path] = None):
        """
        Initialize the abbreviation expander.

        Args:
            abbr_file: Path to abbreviation data file
        """
        if abbr_file is None:
            abbr_file = config.ABBR_DATA_FILE

        self.abbr_file = abbr_file
        self.abbreviations = self._load_abbreviations()

    def _load_abbreviations(self) -> dict:
        """
        Load abbreviations from file.

        Returns:
            Dictionary mapping abbreviations to full forms
        """
        abbr_dict = {}
        if not self.abbr_file.exists():
            logger.warning(f"Abbreviation file not found: {self.abbr_file}")
            return abbr_dict

        try:
            with open(self.abbr_file, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read().split('\n')

            for line in text:
                if '\x97' in line:
                    # Split on the special character (em dash)
                    parts = line.split('\x97')
                    if len(parts) >= 2:
                        abbr = parts[0].strip().upper()
                        full_form = parts[1].strip()
                        abbr_dict[abbr] = full_form

            logger.info(f"Loaded {len(abbr_dict)} abbreviations")
        except Exception as e:
            logger.error(f"Error loading abbreviations: {e}")

        return abbr_dict

    def get_full_form(self, abbr: str) -> Optional[str]:
        """
        Get the full form of an abbreviation.

        Args:
            abbr: Abbreviation to expand

        Returns:
            Full form of the abbreviation, or None if not found
        """
        abbr = abbr.upper().strip()
        full_form = self.abbreviations.get(abbr)

        if full_form:
            logger.info(f"Found abbreviation: {abbr} -> {full_form}")
        else:
            logger.warning(f"Abbreviation not found: {abbr}")

        return full_form

    def extract_abbreviation_from_question(self, question: str) -> Optional[str]:
        """
        Extract the abbreviation from a question.

        Args:
            question: Question asking about an abbreviation

        Returns:
            Extracted abbreviation, or None if not found
        """
        # Remove spaces for easier parsing
        q = re.sub(r' ', '', question)

        # Look for patterns like "what is the full form of XYZ"
        if 'of' in q:
            match = re.search(r'of([A-Z]+)\??', q, re.IGNORECASE)
            if match:
                return match.group(1)

        # Look for patterns like "what does XYZ stand for"
        if 'does' in q:
            match = re.search(r'does([A-Z]+)stand', q, re.IGNORECASE)
            if match:
                return match.group(1)

        # Look for all-caps words in the question
        words = question.split()
        for word in words:
            # Strip punctuation
            clean_word = re.sub(r'[^A-Z]', '', word.upper())
            if clean_word and len(clean_word) >= 2 and clean_word.isupper():
                return clean_word

        logger.warning(f"Could not extract abbreviation from: {question}")
        return None

    def answer_abbreviation(self, question: str) -> Optional[str]:
        """
        Answer an abbreviation expansion question.

        Args:
            question: Question asking about an abbreviation

        Returns:
            Full form of the abbreviation, or None if not found
        """
        logger.info(f"Processing abbreviation question: {question}")
        abbr = self.extract_abbreviation_from_question(question)

        if abbr:
            logger.info(f"Extracted abbreviation: {abbr}")
            return self.get_full_form(abbr)

        return None


def answer_abbreviations(question: str) -> Optional[str]:
    """
    Legacy function for backward compatibility.

    Args:
        question: Question asking about an abbreviation

    Returns:
        Full form of the abbreviation
    """
    expander = AbbreviationExpander()
    return expander.answer_abbreviation(question)
