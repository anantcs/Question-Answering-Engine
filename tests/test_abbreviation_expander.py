"""Unit tests for abbreviation expander."""
import unittest
from pathlib import Path
from src.processing.abbreviation_expander import AbbreviationExpander


class TestAbbreviationExpander(unittest.TestCase):
    """Test cases for AbbreviationExpander."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary abbreviation file for testing
        self.test_abbr_file = Path("tests/test_abbr.txt")
        self.test_abbr_file.parent.mkdir(exist_ok=True)

        with open(self.test_abbr_file, 'w', encoding='utf-8') as f:
            f.write("NASA\x97National Aeronautics and Space Administration\n")
            f.write("HTML\x97HyperText Markup Language\n")
            f.write("CPU\x97Central Processing Unit\n")
            f.write("AI\x97Artificial Intelligence\n")

        self.expander = AbbreviationExpander(self.test_abbr_file)

    def tearDown(self):
        """Clean up test files."""
        if self.test_abbr_file.exists():
            self.test_abbr_file.unlink()

    def test_get_full_form(self):
        """Test getting full form of abbreviation."""
        result = self.expander.get_full_form("NASA")
        self.assertEqual(result, "National Aeronautics and Space Administration")

        result = self.expander.get_full_form("HTML")
        self.assertEqual(result, "HyperText Markup Language")

    def test_get_full_form_case_insensitive(self):
        """Test that abbreviation lookup is case-insensitive."""
        result = self.expander.get_full_form("nasa")
        self.assertEqual(result, "National Aeronautics and Space Administration")

        result = self.expander.get_full_form("html")
        self.assertEqual(result, "HyperText Markup Language")

    def test_get_full_form_not_found(self):
        """Test handling of unknown abbreviations."""
        result = self.expander.get_full_form("XYZ")
        self.assertIsNone(result)

    def test_extract_abbreviation_with_of(self):
        """Test extracting abbreviation from 'of' pattern."""
        question = "what is the full form of NASA?"
        result = self.expander.extract_abbreviation_from_question(question)
        self.assertEqual(result, "NASA")

    def test_extract_abbreviation_with_stands_for(self):
        """Test extracting abbreviation from 'stands for' pattern."""
        question = "what does HTML stand for?"
        result = self.expander.extract_abbreviation_from_question(question)
        self.assertEqual(result, "HTML")

    def test_extract_abbreviation_from_caps_word(self):
        """Test extracting all-caps word."""
        question = "expand CPU please"
        result = self.expander.extract_abbreviation_from_question(question)
        self.assertEqual(result, "CPU")

    def test_answer_abbreviation_complete(self):
        """Test complete abbreviation answering."""
        question = "what is the full form of AI?"
        result = self.expander.answer_abbreviation(question)
        self.assertEqual(result, "Artificial Intelligence")


if __name__ == '__main__':
    unittest.main()
