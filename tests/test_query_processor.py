"""Unit tests for query processor."""
import unittest
from src.processing.query_processor import QueryProcessor


class TestQueryProcessor(unittest.TestCase):
    """Test cases for QueryProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = QueryProcessor()

    def test_clean_removes_punctuation(self):
        """Test that punctuation is removed."""
        question = "Who is the president?"
        result = self.processor.clean(question)
        self.assertEqual(result, "Who is the president")

    def test_remove_stopwords(self):
        """Test stopword removal."""
        question = "who is the president of india"
        result = self.processor.remove_stopwords(question)

        # 'who', 'is', 'the', 'of' are stopwords
        self.assertIn('president', result)
        self.assertIn('india', result)
        self.assertNotIn('the', [w.lower() for w in result])
        self.assertNotIn('of', [w.lower() for w in result])

    def test_process_query_complete(self):
        """Test complete query processing."""
        question = "Where did Sachin Tendulkar score his first century?"
        result = self.processor.process_query(question)

        # Should contain important keywords
        result_lower = [w.lower() for w in result]
        self.assertIn('sachin', result_lower)
        self.assertIn('tendulkar', result_lower)
        self.assertIn('score', result_lower)
        self.assertIn('first', result_lower)
        self.assertIn('century', result_lower)

        # Should not contain stopwords
        self.assertNotIn('did', result_lower)
        self.assertNotIn('his', result_lower)

    def test_empty_question(self):
        """Test handling of empty questions."""
        result = self.processor.process_query("")
        self.assertEqual(result, [])

    def test_question_with_only_stopwords(self):
        """Test question with only stopwords."""
        question = "is the a an"
        result = self.processor.process_query(question)
        # Should return empty or very few words
        self.assertLessEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()
