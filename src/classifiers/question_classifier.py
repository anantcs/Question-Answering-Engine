"""Question classification module."""
import re
from typing import Optional, Tuple, List, Dict
import nltk
from pathlib import Path

from ..utils.config import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class QuestionClassifier:
    """Classifies questions to determine expected answer type."""

    # Answer type constants
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    DATE = "DATE"
    ENTITY = "ENTY"
    DESCRIPTION = "DESC"
    ABBREVIATION = "ABBR"
    NUMBER = "NUM"
    HUMAN = "HUM"

    def __init__(self):
        """Initialize the question classifier."""
        self.classifier = None

    def classify_rule_based(self, question: str) -> str:
        """
        Classify question using simple rule-based approach.

        Args:
            question: Input question string

        Returns:
            Expected answer type
        """
        question = question.lower().strip()

        # Check for abbreviation questions
        abbr_patterns = ['full form', 'stands for', 'stand for', 'acronym', 'abbreviation']
        if any(pattern in question for pattern in abbr_patterns):
            logger.info("Classified as ABBREVIATION")
            return self.ABBREVIATION

        # Check first word for common question types
        words = question.split()
        if not words:
            logger.warning("Empty question provided")
            return self.DESCRIPTION

        first_word = words[0]

        if first_word == "who":
            logger.info("Classified as PERSON (who)")
            return self.PERSON
        elif first_word == "where":
            logger.info("Classified as LOCATION (where)")
            return self.LOCATION
        elif first_word == "when":
            logger.info("Classified as DATE (when)")
            return self.DATE
        elif first_word == "how" and len(words) > 1:
            second_word = words[1]
            if second_word in ["many", "much", "long", "far", "old"]:
                logger.info("Classified as NUMBER (how many/much)")
                return self.NUMBER
            else:
                logger.info("Classified as DESCRIPTION (how)")
                return self.DESCRIPTION
        elif first_word in ["what", "which"]:
            # Check for specific patterns
            if "definition" in question or "mean" in question:
                logger.info("Classified as DESCRIPTION (definition)")
                return self.DESCRIPTION
            else:
                logger.info("Classified as ENTITY (what/which)")
                return self.ENTITY
        elif first_word == "why":
            logger.info("Classified as DESCRIPTION (why)")
            return self.DESCRIPTION
        elif first_word in ["is", "are", "was", "were", "do", "does", "did", "can", "could"]:
            logger.info("Classified as DESCRIPTION (boolean)")
            return self.DESCRIPTION
        else:
            logger.info("Classified as DESCRIPTION (default)")
            return self.DESCRIPTION

    def load_training_data(self, training_file: Optional[Path] = None) -> Tuple[List[str], List[str]]:
        """
        Load training data from file.

        Args:
            training_file: Path to training data file

        Returns:
            Tuple of (questions, labels)
        """
        if training_file is None:
            training_file = config.TRAINING_SET_FILE

        if not training_file.exists():
            logger.warning(f"Training file not found: {training_file}")
            return [], []

        try:
            with open(training_file, 'r', encoding='utf-8') as f:
                lines = f.read().split('\n')

            questions = []
            labels = []

            for line in lines:
                line = line.strip()
                if not line or line.startswith('ABBR'):
                    continue

                # Extract label (first word) and question (rest)
                parts = line.split(' ', 1)
                if len(parts) < 2:
                    continue

                # Remove subclasses from label (e.g., "NUM:date" -> "NUM")
                label = re.sub(r':[a-z]+', '', parts[0])
                question = parts[1]

                questions.append(question)
                labels.append(label)

            logger.info(f"Loaded {len(questions)} training examples")
            return questions, labels

        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return [], []

    def extract_features(self, question: str) -> Dict[str, bool]:
        """
        Extract features from a question for ML classification.

        Args:
            question: Input question

        Returns:
            Feature dictionary
        """
        features = {}

        # Tokenize
        try:
            tokens = nltk.word_tokenize(question.lower())
        except LookupError:
            nltk.download('punkt', quiet=True)
            tokens = nltk.word_tokenize(question.lower())

        # Bag of words features
        for word in tokens:
            features[f'contains({word})'] = True

        # Positional features
        if len(tokens) >= 1:
            features['first_word'] = tokens[0]
        if len(tokens) >= 2:
            features['second_word'] = tokens[1]
        if len(tokens) >= 3:
            features['third_word'] = tokens[2]

        return features

    def train_classifier(self, training_file: Optional[Path] = None) -> Optional[object]:
        """
        Train a Naive Bayes classifier on training data.

        Args:
            training_file: Path to training data file

        Returns:
            Trained classifier or None if training fails
        """
        questions, labels = self.load_training_data(training_file)

        if not questions:
            logger.warning("No training data available")
            return None

        try:
            # Create feature sets
            featuresets = [
                (self.extract_features(q), label)
                for q, label in zip(questions, labels)
            ]

            # Split into train and test
            split_point = int(len(featuresets) * 0.8)
            train_set = featuresets[split_point:]
            test_set = featuresets[:split_point]

            # Train classifier
            classifier = nltk.NaiveBayesClassifier.train(train_set)

            # Evaluate
            accuracy = nltk.classify.accuracy(classifier, test_set)
            logger.info(f"Classifier accuracy: {accuracy:.2%}")

            self.classifier = classifier
            return classifier

        except Exception as e:
            logger.error(f"Error training classifier: {e}")
            return None

    def classify_ml(self, question: str) -> str:
        """
        Classify question using trained ML classifier.

        Args:
            question: Input question

        Returns:
            Expected answer type
        """
        if self.classifier is None:
            logger.warning("Classifier not trained. Training now...")
            self.train_classifier()

        if self.classifier is None:
            logger.warning("ML classification failed. Using rule-based fallback")
            return self.classify_rule_based(question)

        try:
            features = self.extract_features(question)
            question_type = self.classifier.classify(features)

            # Map to answer type
            answer_type = self._map_question_type_to_answer_type(question_type, question)
            logger.info(f"ML classified as: {answer_type}")
            return answer_type

        except Exception as e:
            logger.error(f"ML classification error: {e}. Using rule-based fallback")
            return self.classify_rule_based(question)

    def _map_question_type_to_answer_type(self, question_type: str, question: str) -> str:
        """
        Map ML question type to NER answer type.

        Args:
            question_type: Question type from classifier
            question: Original question

        Returns:
            Expected answer type for NER
        """
        type_map = {
            "DESC": self.DESCRIPTION,
            "ENTY": self.ENTITY,
            "HUM": self.PERSON,
            "LOC": self.LOCATION,
            "ABBR": self.ABBREVIATION,
        }

        if question_type == "NUM":
            # Check if it's asking for a date
            if "when" in question.lower():
                return self.DATE
            else:
                return self.NUMBER

        return type_map.get(question_type, self.DESCRIPTION)

    def classify(self, question: str, use_ml: bool = False) -> str:
        """
        Classify a question to determine expected answer type.

        Args:
            question: Input question
            use_ml: Whether to use ML classifier (default: False)

        Returns:
            Expected answer type
        """
        logger.info(f"Classifying question: {question}")

        if use_ml:
            return self.classify_ml(question)
        else:
            return self.classify_rule_based(question)


# Legacy functions for backward compatibility
def ret_answer_type(question: str) -> str:
    """
    Get answer type for a question (rule-based).

    Args:
        question: Input question

    Returns:
        Expected answer type
    """
    classifier = QuestionClassifier()
    return classifier.classify_rule_based(question)


def ret_answer_type2(question: str) -> str:
    """
    Get answer type for a question (ML-based).

    Args:
        question: Input question

    Returns:
        Expected answer type
    """
    classifier = QuestionClassifier()
    return classifier.classify_ml(question)
