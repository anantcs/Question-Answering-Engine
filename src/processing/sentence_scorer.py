"""Sentence scoring and ranking module."""
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from ..utils.config import config
from ..utils.logger import setup_logger
from .answer_extractor import AnswerExtractor

logger = setup_logger(__name__)


class SentenceScorer:
    """Scores and ranks sentences based on query and answer type."""

    def __init__(self):
        """Initialize the sentence scorer."""
        self.answer_extractor = AnswerExtractor()

    def score_sentence(self, sentence: str, query: List[str]) -> int:
        """
        Calculate relevance score for a sentence.

        Args:
            sentence: Sentence text
            query: List of query keywords

        Returns:
            Relevance score (unique keyword count)
        """
        sentence_lower = sentence.lower()
        words = sentence_lower.split()

        # Count unique keywords present
        keyword_dict = {}
        for word in words:
            for keyword in query:
                if word == keyword.lower():
                    keyword_dict[keyword] = True

        # Score is the number of unique keywords
        score = len(keyword_dict)
        return score

    def filter_sentences_by_entity_type(
        self,
        sentences: List[str],
        tagged_sentences: List[str],
        answer_type: str
    ) -> List[int]:
        """
        Filter sentences that contain the expected entity type.

        Args:
            sentences: List of sentences
            tagged_sentences: NER-tagged sentences
            answer_type: Expected answer type

        Returns:
            List of 1s and 0s indicating which sentences contain the answer type
        """
        entity_filter = []

        for tagged_sent in tagged_sentences:
            if f'/{answer_type}' in tagged_sent:
                entity_filter.append(1)
            else:
                entity_filter.append(0)

        logger.debug(f"Entity filter: {entity_filter}")
        return entity_filter

    def score_filtered_sentences(
        self,
        sentences: List[str],
        query: List[str],
        entity_filter: List[int]
    ) -> Dict[int, int]:
        """
        Score sentences that pass the entity filter.

        Args:
            sentences: List of sentences
            query: Query keywords
            entity_filter: Binary filter indicating valid sentences

        Returns:
            Dictionary mapping sentence index to score
        """
        scores = {}
        sentence_count = 0

        for idx, sentence in enumerate(sentences):
            if idx >= len(entity_filter):
                break

            if entity_filter[idx] == 0:
                # Sentence doesn't contain the answer type
                scores[idx] = 0
            else:
                # Score the sentence
                sentence_count += 1
                score = self.score_sentence(sentence, query)
                scores[idx] = score
                logger.debug(f"Sentence {idx}: score = {score}")

        logger.info(f"Scored {sentence_count} sentences containing answer type")
        return scores, sentence_count

    def get_ner_tagged_sentences(
        self,
        imp_info_file: Path = None
    ) -> Tuple[Optional[str], List[str]]:
        """
        Get NER-tagged sentences from important info file.

        Args:
            imp_info_file: Path to important info file

        Returns:
            Tuple of (NER HTML response, list of tagged sentences)
        """
        if imp_info_file is None:
            imp_info_file = config.IMP_INFO_FILE

        if not imp_info_file.exists():
            logger.error(f"Important info file not found: {imp_info_file}")
            return None, []

        try:
            with open(imp_info_file, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info("Getting NER tags for important paragraphs")
            ner_html = self.answer_extractor.get_ner_tags(content)

            if not ner_html:
                logger.error("Failed to get NER tags")
                return None, []

            # Extract tagged text
            tagged_text = self.answer_extractor.extract_tagged_text_from_html(ner_html)
            tagged_sentences = tagged_text.split('.')

            logger.info(f"Got {len(tagged_sentences)} tagged sentences")
            return tagged_text, tagged_sentences

        except Exception as e:
            logger.error(f"Error getting NER tags: {e}")
            return None, []

    def rank_sentences(self, scores: Dict[int, int]) -> List[Tuple[int, int]]:
        """
        Rank sentences by score in descending order.

        Args:
            scores: Dictionary mapping sentence index to score

        Returns:
            List of (sentence_index, score) tuples, sorted by score
        """
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        logger.info(f"Top sentence scores: {ranked[:5]}")
        return ranked

    def get_max_score_sentences(
        self,
        ranked_scores: List[Tuple[int, int]]
    ) -> Tuple[List[int], int]:
        """
        Get indices of sentences with maximum score.

        Args:
            ranked_scores: Ranked list of (index, score) tuples

        Returns:
            Tuple of (list of top indices, max score)
        """
        if not ranked_scores:
            return [], 0

        max_score = ranked_scores[0][1]
        top_indices = []

        for idx, score in ranked_scores:
            if score == max_score:
                top_indices.append(idx)
            else:
                break

        logger.info(f"Found {len(top_indices)} sentences with max score {max_score}")
        return top_indices, max_score

    def save_important_sentences(
        self,
        top_indices: List[int],
        imp_info_file: Path = None,
        output_file: Path = None
    ) -> None:
        """
        Save important sentences to file.

        Args:
            top_indices: Indices of important sentences
            imp_info_file: Input file with all sentences
            output_file: Output file for important sentences
        """
        if imp_info_file is None:
            imp_info_file = config.IMP_INFO_FILE
        if output_file is None:
            output_file = config.IMP_SENTENCES_FILE

        if not imp_info_file.exists():
            logger.error(f"Input file not found: {imp_info_file}")
            return

        try:
            with open(imp_info_file, 'r', encoding='utf-8') as f:
                content = f.read()
            sentences = content.split('.')

            with open(output_file, 'w', encoding='utf-8') as f:
                for idx in top_indices:
                    if idx < len(sentences):
                        f.write(sentences[idx] + '.')

            logger.info(f"Saved {len(top_indices)} important sentences to {output_file}")

        except Exception as e:
            logger.error(f"Error saving important sentences: {e}")

    def process(
        self,
        query: List[str],
        answer_type: str
    ) -> Tuple[List[str], List[int], int, int]:
        """
        Complete sentence scoring pipeline.

        Args:
            query: List of query keywords
            answer_type: Expected answer type

        Returns:
            Tuple of (tagged_sentences, important_indices, max_score, single_sentence_flag)
        """
        logger.info("Starting sentence scoring")

        # Get NER-tagged sentences
        tagged_text, tagged_sentences = self.get_ner_tagged_sentences()

        if not tagged_sentences:
            logger.error("No tagged sentences available")
            return [], [], 0, 0

        # Read original sentences
        imp_info_file = config.IMP_INFO_FILE
        try:
            with open(imp_info_file, 'r', encoding='utf-8') as f:
                content = f.read()
            sentences = content.split('.')
        except Exception as e:
            logger.error(f"Error reading sentences: {e}")
            return tagged_sentences, [], 0, 0

        # Filter by entity type
        entity_filter = self.filter_sentences_by_entity_type(
            sentences,
            tagged_sentences,
            answer_type
        )

        # Score sentences
        scores, sentence_count = self.score_filtered_sentences(
            sentences,
            query,
            entity_filter
        )

        # Check if only one sentence contains the answer type
        single_sentence_flag = 1 if sentence_count == 1 else 0

        # Rank sentences
        ranked = self.rank_sentences(scores)

        # Get top sentences
        top_indices, max_score = self.get_max_score_sentences(ranked)

        # Save important sentences
        if top_indices:
            self.save_important_sentences(top_indices)

        logger.info("Sentence scoring completed")
        return tagged_sentences, top_indices, max_score, single_sentence_flag


# Legacy function for backward compatibility
def score_sentences(
    query: List[str],
    answer_type: str
) -> Tuple[List[str], List[int], int, int]:
    """
    Score and rank sentences (legacy function).

    Args:
        query: List of query keywords
        answer_type: Expected answer type

    Returns:
        Tuple of (tagged_sentences, important_indices, max_score, single_sentence_flag)
    """
    scorer = SentenceScorer()
    return scorer.process(query, answer_type)
