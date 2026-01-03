"""Answer extraction and processing module."""
import re
from typing import List, Optional, Tuple
import requests
import nltk

from ..utils.config import config
from ..utils.logger import setup_logger
from .abbreviation_expander import AbbreviationExpander

logger = setup_logger(__name__)


class AnswerExtractor:
    """Extracts answers from sentences using NER."""

    def __init__(self):
        """Initialize the answer extractor."""
        self.stanford_ner_url = config.STANFORD_NER_URL
        self.timeout = config.REQUEST_TIMEOUT

    def get_ner_tags(self, text: str) -> Optional[str]:
        """
        Get NER tags from Stanford NER service.

        Args:
            text: Input text to tag

        Returns:
            Tagged text in slash format, or None if request fails
        """
        try:
            logger.info("Requesting NER tags from Stanford NER service")

            # Prepare form data
            data = {
                'input': text,
                'outputFormat': 'slashTags'
            }

            # Make request
            response = requests.post(
                self.stanford_ner_url,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            logger.info("Successfully received NER tags")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Error getting NER tags: {e}")
            logger.warning("NER service unavailable. Answer extraction may be limited.")
            return None

    def extract_tagged_text_from_html(self, html: str) -> str:
        """
        Extract the tagged text from Stanford NER HTML response.

        Args:
            html: HTML response from Stanford NER

        Returns:
            Extracted tagged text
        """
        try:
            # Find the tagged output in the HTML
            s1 = html.find('</FORM>')
            s2 = html.find('</div>', s1 + 1)
            s3 = html.find('</div>', s2 + 1)
            s4 = html.find('</div>', s3 + 1)
            s5 = html.find('\n', s4)
            s6 = html.find('<div id', s5 + 1)

            if s6 == -1:
                # Try alternative ending
                s6 = html.find('.', s5 + 1)
                if s6 != -1:
                    s6 += 1

            return html[s5 + 1:s6]

        except Exception as e:
            logger.error(f"Error extracting tagged text: {e}")
            return ""

    def parse_tagged_answer(self, tagged_text: str, answer_type: str) -> str:
        """
        Parse and extract answer from tagged text.

        Args:
            tagged_text: NER-tagged text with slash format (word/TAG)
            answer_type: Expected answer type (PERSON, LOCATION, DATE, etc.)

        Returns:
            Extracted answer string
        """
        # Remove the answer type tag and slashes
        answer = tagged_text.replace(f'/{answer_type}', '')
        answer = re.sub(r'/', '', answer)
        answer = answer.strip()

        logger.info(f"Extracted answer: {answer}")
        return answer

    def extract_answer_from_sentence(
        self,
        sentence: str,
        answer_type: str
    ) -> Optional[str]:
        """
        Extract answer of specific type from a sentence.

        Args:
            sentence: Input sentence
            answer_type: Expected answer type

        Returns:
            Extracted answer, or None if not found
        """
        # Get NER tags
        ner_html = self.get_ner_tags(sentence)
        if not ner_html:
            logger.warning("Could not get NER tags")
            return None

        # Extract tagged text
        tagged_text = self.extract_tagged_text_from_html(ner_html)
        if not tagged_text:
            logger.warning("Could not extract tagged text")
            return None

        # Split into sentences
        tagged_sentences = tagged_text.split('.')

        # Find answer in tagged sentences
        answer = ""
        for tagged_sentence in tagged_sentences:
            tokens = nltk.word_tokenize(tagged_sentence)

            # Look for tokens with the answer type tag
            collecting = False
            for token in tokens:
                if f'/{answer_type}' in token:
                    collecting = True
                    # Remove the tag
                    clean_token = token.replace(f'/{answer_type}', '')
                    clean_token = re.sub(r'/[A-Z]+', '', clean_token)
                    answer += clean_token + ' '
                elif collecting and '/' not in token:
                    # Continue collecting words without tags
                    answer += token + ' '
                elif collecting and '/' in token:
                    # Hit a different tag, stop collecting
                    return answer.strip()

            if answer:
                return answer.strip()

        return None

    def extract_answers_from_sentences(
        self,
        sentences: List[str],
        answer_type: str,
        tagged_sentences: List[str],
        important_indices: List[int]
    ) -> Optional[str]:
        """
        Extract answer from multiple sentences.

        Args:
            sentences: List of candidate sentences
            answer_type: Expected answer type
            tagged_sentences: Pre-tagged sentences from NER
            important_indices: Indices of important sentences

        Returns:
            Best answer found, or None
        """
        for i, sentence in enumerate(sentences):
            if i >= len(important_indices):
                break

            idx = important_indices[i]
            if idx >= len(tagged_sentences):
                continue

            tagged_sentence = tagged_sentences[idx]

            # Parse answer from tagged sentence
            answer_parts = []
            for token in nltk.word_tokenize(tagged_sentence):
                if f'/{answer_type}' in token:
                    clean_token = self.parse_tagged_answer(token, answer_type)
                    if clean_token:
                        answer_parts.append(clean_token)

            if answer_parts:
                answer = ' '.join(answer_parts)
                logger.info(f"Found answer: {answer}")
                return answer

        return None

    def process_answer(
        self,
        answer_type: str,
        question: str,
        tagged_sentences: List[str],
        important_indices: List[int]
    ) -> Optional[str]:
        """
        Main answer processing pipeline.

        Args:
            answer_type: Expected answer type
            question: Original question
            tagged_sentences: NER-tagged sentences
            important_indices: Indices of important sentences

        Returns:
            Final answer, or None if not found
        """
        logger.info(f"Processing answer for type: {answer_type}")

        # Handle abbreviations separately
        if answer_type == "ABBR":
            expander = AbbreviationExpander()
            return expander.answer_abbreviation(question)

        # Read important sentences
        imp_sentences_file = config.IMP_SENTENCES_FILE
        if not imp_sentences_file.exists():
            logger.error(f"Important sentences file not found: {imp_sentences_file}")
            return None

        try:
            with open(imp_sentences_file, 'r', encoding='utf-8') as f:
                content = f.read()
            sentences = content.split('.')

            # Extract answer
            answer = self.extract_answers_from_sentences(
                sentences,
                answer_type,
                tagged_sentences,
                important_indices
            )

            return answer

        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            return None


# Legacy function for backward compatibility
def NER_string(text: str) -> Optional[str]:
    """
    Get NER tags for text (legacy function).

    Args:
        text: Input text

    Returns:
        NER-tagged HTML response
    """
    extractor = AnswerExtractor()
    return extractor.get_ner_tags(text)


def answer_processing(
    answer_type: str,
    question: str,
    final: List[str],
    imp_sentences: List[int]
) -> Optional[str]:
    """
    Process and extract answer (legacy function).

    Args:
        answer_type: Expected answer type
        question: Original question
        final: Tagged sentences
        imp_sentences: Important sentence indices

    Returns:
        Extracted answer
    """
    extractor = AnswerExtractor()
    return extractor.process_answer(answer_type, question, final, imp_sentences)
