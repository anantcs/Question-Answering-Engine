"""Paragraph scoring and ranking module."""
from typing import List, Dict, Tuple
from pathlib import Path

from ..utils.config import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ParagraphScorer:
    """Scores and ranks paragraphs based on query relevance."""

    def __init__(self):
        """Initialize the paragraph scorer."""
        self.top_k = config.TOP_PARAGRAPHS

    def score_paragraph(self, paragraph: str, query: List[str]) -> int:
        """
        Calculate relevance score for a paragraph.

        Args:
            paragraph: Paragraph text
            query: List of query keywords

        Returns:
            Relevance score (keyword frequency count)
        """
        paragraph_lower = paragraph.lower()
        words = paragraph_lower.split()

        # Count keyword occurrences
        keyword_counts = {}
        for word in words:
            for keyword in query:
                if word == keyword.lower():
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        # Total score is sum of all keyword occurrences
        score = sum(keyword_counts.values())
        return score

    def read_and_score_paragraphs(
        self,
        query: List[str],
        para_file: Path = None
    ) -> Dict[int, int]:
        """
        Read paragraphs from file and score them.

        Args:
            query: List of query keywords
            para_file: Path to paragraph file

        Returns:
            Dictionary mapping paragraph index to score
        """
        if para_file is None:
            para_file = config.PARA_FILE

        if not para_file.exists():
            logger.error(f"Paragraph file not found: {para_file}")
            return {}

        try:
            with open(para_file, 'r', encoding='utf-8') as f:
                content = f.read()
            paragraphs = content.split('\n\n')

            logger.info(f"Scoring {len(paragraphs)} paragraphs")

            scores = {}
            for idx, para in enumerate(paragraphs):
                if para.strip():  # Skip empty paragraphs
                    score = self.score_paragraph(para, query)
                    scores[idx] = score
                    logger.debug(f"Paragraph {idx}: score = {score}")

            return scores

        except Exception as e:
            logger.error(f"Error reading paragraphs: {e}")
            return {}

    def rank_paragraphs(self, scores: Dict[int, int]) -> List[Tuple[int, int]]:
        """
        Rank paragraphs by score in descending order.

        Args:
            scores: Dictionary mapping paragraph index to score

        Returns:
            List of (paragraph_index, score) tuples, sorted by score
        """
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        logger.info(f"Top scores: {ranked[:5]}")
        return ranked

    def save_top_paragraphs(
        self,
        ranked_scores: List[Tuple[int, int]],
        para_file: Path = None,
        output_file: Path = None
    ) -> None:
        """
        Save top-k paragraphs to output file.

        Args:
            ranked_scores: List of (paragraph_index, score) tuples
            para_file: Input paragraph file
            output_file: Output file for top paragraphs
        """
        if para_file is None:
            para_file = config.PARA_FILE
        if output_file is None:
            output_file = config.IMP_INFO_FILE

        if not para_file.exists():
            logger.error(f"Paragraph file not found: {para_file}")
            return

        try:
            # Read all paragraphs
            with open(para_file, 'r', encoding='utf-8') as f:
                content = f.read()
            paragraphs = content.split('\n\n')

            # Get indices of top paragraphs
            top_indices = [idx for idx, _ in ranked_scores[:self.top_k]]

            # Write top paragraphs
            with open(output_file, 'w', encoding='utf-8') as f:
                for idx in top_indices:
                    if idx < len(paragraphs):
                        f.write(paragraphs[idx])
                        f.write('\n\n')

            logger.info(f"Saved top {len(top_indices)} paragraphs to {output_file}")

        except Exception as e:
            logger.error(f"Error saving top paragraphs: {e}")

    def process(self, query: List[str]) -> None:
        """
        Complete paragraph scoring pipeline.

        Args:
            query: List of query keywords
        """
        logger.info("Starting paragraph scoring")

        # Score paragraphs
        scores = self.read_and_score_paragraphs(query)

        if not scores:
            logger.error("No paragraphs to score")
            return

        # Rank paragraphs
        ranked = self.rank_paragraphs(scores)

        # Save top paragraphs
        self.save_top_paragraphs(ranked)

        logger.info("Paragraph scoring completed")


# Legacy function for backward compatibility
def score_paras(query: List[str]) -> None:
    """
    Score and rank paragraphs (legacy function).

    Args:
        query: List of query keywords
    """
    scorer = ParagraphScorer()
    scorer.process(query)
