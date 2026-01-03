"""Unit tests for question classifier."""
import unittest
from src.classifiers.question_classifier import QuestionClassifier


class TestQuestionClassifier(unittest.TestCase):
    """Test cases for QuestionClassifier."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = QuestionClassifier()

    def test_classify_who_question(self):
        """Test classification of 'who' questions."""
        question = "who is the president of india?"
        result = self.classifier.classify_rule_based(question)
        self.assertEqual(result, QuestionClassifier.PERSON)

    def test_classify_where_question(self):
        """Test classification of 'where' questions."""
        question = "where did sachin score his first century?"
        result = self.classifier.classify_rule_based(question)
        self.assertEqual(result, QuestionClassifier.LOCATION)

    def test_classify_when_question(self):
        """Test classification of 'when' questions."""
        question = "when did the first person land on the moon?"
        result = self.classifier.classify_rule_based(question)
        self.assertEqual(result, QuestionClassifier.DATE)

    def test_classify_abbreviation_question(self):
        """Test classification of abbreviation questions."""
        questions = [
            "what is the full form of nasa?",
            "what does html stand for?",
            "expand the acronym cpu"
        ]
        for question in questions:
            result = self.classifier.classify_rule_based(question)
            self.assertEqual(result, QuestionClassifier.ABBREVIATION)

    def test_classify_how_many_question(self):
        """Test classification of 'how many' questions."""
        question = "how many people live in china?"
        result = self.classifier.classify_rule_based(question)
        self.assertEqual(result, QuestionClassifier.NUMBER)

    def test_classify_what_question(self):
        """Test classification of 'what' questions."""
        question = "what is the capital of france?"
        result = self.classifier.classify_rule_based(question)
        self.assertEqual(result, QuestionClassifier.ENTITY)

    def test_classify_why_question(self):
        """Test classification of 'why' questions."""
        question = "why is the sky blue?"
        result = self.classifier.classify_rule_based(question)
        self.assertEqual(result, QuestionClassifier.DESCRIPTION)

    def test_extract_features(self):
        """Test feature extraction."""
        question = "who is the president?"
        features = self.classifier.extract_features(question)

        self.assertIn('contains(who)', features)
        self.assertIn('contains(president)', features)
        self.assertEqual(features['first_word'], 'who')

    def test_empty_question(self):
        """Test handling of empty questions."""
        result = self.classifier.classify_rule_based("")
        self.assertEqual(result, QuestionClassifier.DESCRIPTION)


if __name__ == '__main__':
    unittest.main()
