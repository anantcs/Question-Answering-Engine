"""
Main Question-Answering Engine.

This module orchestrates the complete QA pipeline:
1. Question Classification
2. Information Retrieval
3. Query Formulation
4. Paragraph Scoring
5. Sentence Scoring
6. Answer Extraction
"""
import sys
from typing import Optional

from src.classifiers.question_classifier import QuestionClassifier
from src.retrieval.information_retriever import InformationRetriever
from src.processing.query_processor import QueryProcessor
from src.processing.paragraph_scorer import ParagraphScorer
from src.processing.sentence_scorer import SentenceScorer
from src.processing.answer_extractor import AnswerExtractor
from src.utils.config import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class QuestionAnsweringEngine:
    """Main QA Engine class."""

    def __init__(self):
        """Initialize the QA engine with all components."""
        self.classifier = QuestionClassifier()
        self.retriever = InformationRetriever()
        self.query_processor = QueryProcessor()
        self.paragraph_scorer = ParagraphScorer()
        self.sentence_scorer = SentenceScorer()
        self.answer_extractor = AnswerExtractor()

    def answer_question(self, question: str) -> Optional[str]:
        """
        Answer a question using the complete QA pipeline.

        Args:
            question: Input question string

        Returns:
            Answer string, or None if answer not found
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing question: {question}")
        logger.info(f"{'='*60}")

        try:
            # Step 1: Classify the question
            logger.info("\n[1/6] Classifying question...")
            question = question.lower().strip()
            answer_type = self.classifier.classify(question)
            logger.info(f"Answer type: {answer_type}")

            # Step 2: Retrieve information (skip for abbreviations)
            if answer_type != "ABBR":
                logger.info("\n[2/6] Retrieving information from web...")
                success = self.retriever.retrieve_information(question)
                if not success:
                    logger.error("Failed to retrieve information")
                    return None

                # Step 3: Formulate query
                logger.info("\n[3/6] Formulating query keywords...")
                query = self.query_processor.process_query(question)
                logger.info(f"Query keywords: {query}")

                # Step 4: Score paragraphs
                logger.info("\n[4/6] Scoring paragraphs...")
                self.paragraph_scorer.process(query)

                # Step 5: Score sentences
                logger.info("\n[5/6] Scoring sentences...")
                tagged_sentences, imp_indices, max_score, single_flag = \
                    self.sentence_scorer.process(query, answer_type)

                # Step 6: Extract answer
                logger.info("\n[6/6] Extracting answer...")

                if max_score != 0 and single_flag != 1:
                    answer = self.answer_extractor.process_answer(
                        answer_type,
                        question,
                        tagged_sentences,
                        imp_indices
                    )

                    if answer:
                        logger.info(f"✓ Answer found: {answer}")
                        return answer
                    else:
                        # Return relevant information if exact answer not found
                        logger.warning("Exact answer not found. Returning relevant information.")
                        imp_info_file = config.IMP_INFO_FILE
                        if imp_info_file.exists():
                            with open(imp_info_file, 'r', encoding='utf-8') as f:
                                return f"Relevant information:\n{f.read()}"
                        return None
                else:
                    # Return relevant information
                    logger.info("Returning relevant information (single sentence or no score)")
                    imp_info_file = config.IMP_INFO_FILE
                    if imp_info_file.exists():
                        with open(imp_info_file, 'r', encoding='utf-8') as f:
                            return f"Relevant information:\n{f.read()}"
                    return None

            else:
                # Handle abbreviations
                logger.info("\n[2/6] Processing abbreviation...")
                answer = self.answer_extractor.process_answer(
                    answer_type,
                    question,
                    [],
                    []
                )

                if answer:
                    logger.info(f"✓ Answer found: {answer}")
                    return answer
                else:
                    logger.warning("Abbreviation not found in database")
                    return None

        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return None

        finally:
            # Cleanup temporary files
            logger.info("\nCleaning up temporary files...")
            try:
                config.cleanup_temp_files()
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")

    def interactive_mode(self):
        """Run the QA engine in interactive mode."""
        print("\n" + "="*60)
        print("Question-Answering Engine - Interactive Mode")
        print("="*60)
        print("\nAsk me factual questions!")
        print("Supported types: Who, Where, When, What, Abbreviations")
        print("Type 'quit' or 'exit' to stop.\n")

        while True:
            try:
                question = input("Question: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if not question:
                    continue

                answer = self.answer_question(question)

                if answer:
                    print(f"\nAnswer: {answer}\n")
                else:
                    print("\nSorry, I couldn't find an answer to that question.\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\nError: {e}\n")


def main():
    """Main entry point for the QA engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Question-Answering Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python -m src.main

  # Single question
  python -m src.main -q "Who is the president of India?"

  # Batch mode
  python -m src.main -f questions.txt
        """
    )

    parser.add_argument(
        '-q', '--question',
        type=str,
        help='Ask a single question'
    )

    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Process questions from a file (one per line)'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode (default if no arguments)'
    )

    args = parser.parse_args()

    # Initialize engine
    engine = QuestionAnsweringEngine()

    # Single question mode
    if args.question:
        answer = engine.answer_question(args.question)
        if answer:
            print(f"\nAnswer: {answer}")
        else:
            print("\nSorry, I couldn't find an answer.")
        return

    # Batch mode
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                questions = f.readlines()

            for i, question in enumerate(questions, 1):
                question = question.strip()
                if not question:
                    continue

                print(f"\n[{i}/{len(questions)}] Question: {question}")
                answer = engine.answer_question(question)

                if answer:
                    print(f"Answer: {answer}")
                else:
                    print("No answer found.")

        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        return

    # Interactive mode (default)
    engine.interactive_mode()


if __name__ == "__main__":
    main()
