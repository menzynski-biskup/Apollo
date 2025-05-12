# test_pdf_parser.py
import unittest
from unittest.mock import patch, MagicMock
from apollo.data_ingest.pdf_parser import PDFParser
from apollo.data_ingest.cleaner import TextCleaner

class TestPDFParser(unittest.TestCase):

    @patch('pymupdf.open')
    def test_extract_text(self, mock_open):
        # Mock the PDF document and pages
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This is a test text with a hyphenated word: amy-\nloid."
        mock_doc.__enter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        mock_doc.__len__.return_value = 1

        parser = PDFParser()
        result = parser.extract_text("dummy_path.pdf")
        expected = "This is a test text with a hyphenated word: amyloid.\n\n"
        self.assertEqual(result, expected)

    @patch('pymupdf.open')
    def test_extract_by_page(self, mock_open):
        # Mock the PDF document and pages
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page 1 text."
        mock_doc.__enter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        mock_doc.__len__.return_value = 1

        parser = PDFParser()
        result = parser.extract_by_page("dummy_path.pdf")
        expected = ["Page 1 text."]
        self.assertEqual(result, expected)

    @patch('pymupdf.open')
    def test_extract_and_clean_text(self, mock_open):
        # Mock the PDF document and pages
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This is a test text with a hyphenated word: amy-\nloid."
        mock_doc.__enter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        mock_doc.__len__.return_value = 1

        parser = PDFParser()
        cleaner = TextCleaner()
        result = parser.extract_and_clean_text("dummy_path.pdf", cleaner)
        expected = "this is a test text with a hyphenated word: amyloid."
        self.assertEqual(result, expected)

    def test_fix_hyphenated_words(self):
        parser = PDFParser()

        # Test cross-line hyphenation
        text = "This is a test text with a hyphenated word: amy-\nloid."
        result = parser.fix_hyphenated_words(text)
        expected = "This is a test text with a hyphenated word: amyloid."
        self.assertEqual(result, expected)

        # Test same-line hyphenation
        text = "This is a test text with a hyphenated word: amy- loid."
        result = parser.fix_hyphenated_words(text)
        expected = "This is a test text with a hyphenated word: amyloid."
        self.assertEqual(result, expected)

    def test_remove_header_footer(self):
        parser = PDFParser()

        # Test with header and footer
        text = "Journal of Science 2023\nPage 42\n\nThis is the actual content of the article.\nIt spans multiple lines.\n\nCopyright 2023\ndoi:10.1234/js.2023"
        result = parser.remove_header_footer(text, 0, 10)
        expected = "This is the actual content of the article.\nIt spans multiple lines."
        self.assertEqual(result, expected)

        # Test with minimal text (should return unchanged)
        text = "Short text"
        result = parser.remove_header_footer(text, 0, 10)
        self.assertEqual(result, text)

if __name__ == '__main__':
    unittest.main()
