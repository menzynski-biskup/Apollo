# apollo/data_ingest/pdf_parser.py
import pymupdf
from apollo.data_ingest.cleaner import TextCleaner
import re

class PDFParser:
    def __init__(self, remove_linebreaks=True, remove_headers_footers=True):
        self.remove_linebreaks = remove_linebreaks
        self.remove_headers_footers = remove_headers_footers

    def extract_text(self, pdf_path: str) -> str:
        text = ""
        with pymupdf.open(pdf_path) as doc:
            num_pages = len(doc)
            for page_num, page in enumerate(doc):
                page_text = page.get_text()

                # Remove headers and footers if enabled
                if self.remove_headers_footers:
                    page_text = self.remove_header_footer(page_text, page_num, num_pages)

                # Fix broken words due to hyphenation before replacing line breaks
                page_text = self.fix_hyphenated_words(page_text)

                if self.remove_linebreaks:
                    page_text = page_text.replace('\n', ' ').strip()

                text += page_text + "\n\n"
        return text

    def extract_by_page(self, pdf_path: str) -> list:
        pages = []
        with pymupdf.open(pdf_path) as doc:
            num_pages = len(doc)
            for page_num, page in enumerate(doc):
                page_text = page.get_text()

                # Remove headers and footers if enabled
                if self.remove_headers_footers:
                    page_text = self.remove_header_footer(page_text, page_num, num_pages)

                # Fix hyphenated words
                page_text = self.fix_hyphenated_words(page_text)

                pages.append(page_text)
        return pages

    def extract_and_clean_text(self, pdf_path: str, cleaner: TextCleaner) -> str:
        """Pipeline: PDF ➜ Raw Text ➜ Cleaned Text."""
        raw_text = self.extract_text(pdf_path)
        return cleaner.clean(raw_text)

    def fix_hyphenated_words(self, text: str) -> str:
        """Fix words that are split across lines with a hyphen."""
        # Match a hyphen at the end of a word followed by a newline and another word
        # This handles cases like "amy-\nloid" -> "amyloid"
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

        # Also handle hyphenated words within the same line
        # This handles cases like "amy- loid" -> "amyloid"
        text = re.sub(r"(\w+)-\s+(\w+)", r"\1\2", text)

        return text

    def remove_header_footer(self, text: str, page_num: int, total_pages: int) -> str:
        """
        Remove headers and footers from page text.

        Args:
            text (str): The text of the page
            page_num (int): Current page number (0-indexed)
            total_pages (int): Total number of pages in the document

        Returns:
            str: Text with headers and footers removed
        """
        lines = text.split('\n')
        cleaned_lines = []

        # Skip processing if too few lines
        if len(lines) <= 4:
            return text

        # Common patterns in headers/footers
        header_footer_patterns = [
            r"^Page\s+\d+(\s+of\s+\d+)?$",
            r"^\d+$",  # Just a page number
            r"^[A-Za-z]+\s+\d+$",  # Journal name and page number
            r"^Vol\.\s*\d+,?\s*No\.\s*\d+",  # Volume and issue
            r"^https?://",  # URLs
            r"^www\.",  # URLs
            r"^[A-Za-z]+\s+\d{4}$",  # Journal name and year
            r"^Copyright",  # Copyright notices
            r"^doi:",  # DOI references
            r"^ISSN",  # ISSN numbers
            r"^Received:.*Accepted:",  # Submission dates
        ]

        # Check first 2 and last 2 lines for header/footer patterns
        header_lines = 2
        footer_lines = 2

        # Process middle lines (skip potential headers and footers)
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue

            # Skip first few lines (potential headers)
            if i < header_lines:
                if any(re.match(pattern, line.strip()) for pattern in header_footer_patterns):
                    continue

            # Skip last few lines (potential footers)
            if i >= len(lines) - footer_lines:
                if any(re.match(pattern, line.strip()) for pattern in header_footer_patterns):
                    continue

            # Keep the line if it doesn't match header/footer patterns
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)
