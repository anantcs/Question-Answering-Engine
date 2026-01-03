"""Information retrieval module for fetching web search results."""
import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from ..utils.config import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class InformationRetriever:
    """Retrieves information from web search results."""

    def __init__(self):
        """Initialize the information retriever."""
        self.user_agent = config.USER_AGENT
        self.timeout = config.REQUEST_TIMEOUT
        self.max_results = config.MAX_SEARCH_RESULTS

    def clean_paragraph(self, para: str) -> str:
        """
        Clean HTML and unwanted characters from paragraph.

        Args:
            para: Raw paragraph text

        Returns:
            Cleaned paragraph text
        """
        # Remove HTML tags
        para = re.sub(r'<[a-zA-Z0-9/\\\-%#@()!\$:\^`~&|\*\"\'\,\[\]=\+\._ ;?]+>', "", para)

        # Remove reference numbers like [1], [2]
        para = re.sub(r'\[[0-9]+\]', "", para)

        # Remove ellipsis markers
        para = re.sub(r'\[\.\.\.\]', "", para)

        # Remove HTML artifacts
        para = re.sub(r'more>', "", para)
        para = re.sub(r'>', "", para)
        para = re.sub(r'<', "", para)

        # Normalize multiple periods
        para = re.sub(r'[\.]+', ".", para)

        # Remove double newlines
        para = re.sub(r'\n\n', "", para)

        # Remove HTML entities
        para = re.sub(r'#39', "", para)
        para = re.sub(r'&middot', "", para)
        para = re.sub(r'&nbsp', " ", para)
        para = re.sub(r'&quot', '"', para)
        para = re.sub(r'&amp', '&', para)

        # Keep only allowed characters
        para = re.sub(
            r'[^a-zA-Z0-9/\\\-%#@()!\$:\^`~&|\*"\'\,\[\]=\+\._ ;?<>]',
            "",
            para
        )

        # Normalize whitespace
        para = ' '.join(para.split())

        return para

    def fetch_google_results(self, query: str) -> Optional[str]:
        """
        Fetch Google search results page.

        Args:
            query: Search query

        Returns:
            HTML content of search results, or None if request fails
        """
        try:
            # Format query for URL
            formatted_query = query.replace(' ', '+')
            url = f"https://www.google.com/search?q={formatted_query}"

            headers = {
                'User-Agent': self.user_agent
            }

            logger.info(f"Fetching search results for: {query}")
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            logger.info(f"Successfully fetched search results (status: {response.status_code})")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Error fetching search results: {e}")
            return None

    def extract_snippets_from_html(self, html: str) -> List[str]:
        """
        Extract search result snippets from Google HTML.

        Args:
            html: HTML content from Google search

        Returns:
            List of text snippets
        """
        snippets = []

        try:
            # Try parsing with BeautifulSoup first (more robust)
            soup = BeautifulSoup(html, 'html.parser')

            # Google uses various classes for snippets, try multiple
            snippet_classes = ['st', 'VwiC3b', 'yXK7lf', 'MUxGbd', 'yDYNvb']

            for class_name in snippet_classes:
                elements = soup.find_all('span', class_=class_name)
                for elem in elements:
                    text = elem.get_text()
                    if text and len(text) > 20:  # Filter out very short snippets
                        snippets.append(text)

            # Also try the old regex-based extraction as fallback
            if not snippets:
                snippets = self._extract_snippets_regex(html)

            logger.info(f"Extracted {len(snippets)} snippets")

        except Exception as e:
            logger.error(f"Error extracting snippets: {e}")
            # Fallback to regex
            snippets = self._extract_snippets_regex(html)

        return snippets

    def _extract_snippets_regex(self, html: str) -> List[str]:
        """
        Extract snippets using regex (fallback method).

        Args:
            html: HTML content

        Returns:
            List of snippets
        """
        snippets = []
        page = html
        snippet_count = 0

        # Try to find snippets with the old pattern
        while snippet_count < self.max_results:
            start = page.find('<span class="st">')
            if start == -1:
                break

            end = page.find('</span>', start + 1)
            if end == -1:
                break

            text = page[start + 17:end]
            if text:
                snippets.append(text)
                snippet_count += 1

            page = page[end:]

        logger.info(f"Regex extraction found {len(snippets)} snippets")
        return snippets

    def save_paragraphs(self, snippets: List[str], output_file: Optional[str] = None) -> None:
        """
        Save cleaned paragraphs to file.

        Args:
            snippets: List of text snippets
            output_file: Output file path (defaults to config.PARA_FILE)
        """
        if output_file is None:
            output_file = config.PARA_FILE

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for snippet in snippets:
                    cleaned = self.clean_paragraph(snippet)
                    if cleaned:
                        f.write(cleaned)
                        f.write('\n\n')

            logger.info(f"Saved {len(snippets)} paragraphs to {output_file}")

        except Exception as e:
            logger.error(f"Error saving paragraphs: {e}")

    def retrieve_information(self, query: str) -> bool:
        """
        Retrieve information for a query and save to file.

        Args:
            query: Search query

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Retrieving information for query: {query}")

        # Fetch search results
        html = self.fetch_google_results(query)
        if not html:
            logger.error("Failed to fetch search results")
            return False

        # Extract snippets
        snippets = self.extract_snippets_from_html(html)
        if not snippets:
            logger.warning("No snippets extracted from search results")
            return False

        # Save paragraphs
        self.save_paragraphs(snippets)

        logger.info("Information retrieval completed successfully")
        return True


# Legacy function for backward compatibility
def get_all_links(query: str) -> None:
    """
    Legacy function to retrieve information from web.

    Args:
        query: Search query
    """
    retriever = InformationRetriever()
    retriever.retrieve_information(query)
