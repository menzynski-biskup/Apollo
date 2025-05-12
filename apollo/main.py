# apollo/main.py

import os
import argparse
from datetime import datetime
import re

from apollo.data_ingest.pdf_parser import PDFParser
from apollo.data_ingest.cleaner import TextCleaner
from apollo.ner.scientific_extractor import ScientificEntityExtractor
from apollo.data_storage.scientific_data_store import ScientificDataStore

def extract_metadata_from_text(text):
    """
    Extract basic metadata from the text of an article.
    This is a more sophisticated heuristic approach that tries to identify
    the title, authors, journal, and other metadata from scientific papers.

    Args:
        text (str): The text of the article

    Returns:
        dict: Dictionary containing extracted metadata
    """
    metadata = {
        'title': '',
        'authors': '',
        'journal': '',
        'publication_date': datetime.now().strftime('%Y-%m-%d'),
        'doi': ''
    }

    # Split text into lines and paragraphs for analysis
    lines = text.split('\n')
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    # Extract DOI (more robust pattern)
    doi_patterns = [
        r'(?:doi|DOI)[:.]?\s*([0-9.]+/[^\s\n]+)',
        r'(?:https?://)?(?:dx\.)?doi\.org/([0-9.]+/[^\s\n]+)'
    ]

    for pattern in doi_patterns:
        doi_match = re.search(pattern, text)
        if doi_match:
            metadata['doi'] = doi_match.group(1).strip()
            break

    # Extract title using multiple heuristics
    # Scientific titles are typically at the beginning and often in a larger font
    # They're usually followed by author names and affiliations

    # First, try to identify a title block (first few paragraphs before author section)
    title_candidates = []

    # Look at the first few paragraphs
    for i, para in enumerate(paragraphs[:5]):
        # Skip very short paragraphs
        if len(para) < 10:
            continue

        # Skip paragraphs that look like affiliations or emails
        if re.search(r'@|university|institute|department|school', para, re.IGNORECASE):
            continue

        # Skip paragraphs that look like abstracts
        if re.search(r'^abstract', para, re.IGNORECASE):
            break

        # Skip paragraphs with typical non-title patterns
        if re.search(r'(?:received|accepted|published|copyright|doi)', para, re.IGNORECASE):
            continue

        # Good candidate for title
        title_candidates.append(para)

        # Usually only one paragraph is the title
        if len(title_candidates) >= 1:
            break

    # If we found candidates, use the first one
    if title_candidates:
        # Clean up the title (remove line breaks, extra spaces)
        title = re.sub(r'\s+', ' ', title_candidates[0]).strip()
        # Remove any trailing punctuation
        title = re.sub(r'[.,;:]$', '', title).strip()
        metadata['title'] = title
    elif lines and len(lines) > 0:
        # Fallback to first line if no better candidates
        metadata['title'] = lines[0].strip()

    # Extract authors - look for patterns common in author lists
    author_patterns = [
        # Pattern for author lists with commas and "and"
        r'(?:^|\n)([A-Z][a-z]+ [A-Z][a-z]+(?:,\s*[A-Z][a-z]+ [A-Z][a-z]+)*(?:,? and |,? & )[A-Z][a-z]+ [A-Z][a-z]+)',
        # Pattern for author lists with superscript affiliations
        r'(?:^|\n)([A-Z][a-z]+ [A-Z][a-z]+(?:\s*\d+)?(?:,\s*[A-Z][a-z]+ [A-Z][a-z]+(?:\s*\d+)?)*)',
        # Fallback pattern
        r'(?:authors?|by)[:;]?\s*([^\.]+)'
    ]

    for pattern in author_patterns:
        author_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if author_match:
            authors = author_match.group(1).strip()
            # Clean up author list (remove affiliations, extra spaces)
            authors = re.sub(r'\s+', ' ', authors).strip()
            metadata['authors'] = authors
            break

    # Extract journal name - look for common journal citation patterns
    journal_patterns = [
        r'(?:journal|published in)[:;]?\s*([^\.]+)',
        r'(?:[A-Z][a-zA-Z\s]+),\s+vol(?:ume)?\.?\s+\d+',
        r'(?:[A-Z][a-zA-Z\s]+),\s+\d+\s*\(\d+\)'
    ]

    for pattern in journal_patterns:
        journal_match = re.search(pattern, text, re.IGNORECASE)
        if journal_match:
            journal = journal_match.group(1 if 'journal|published' in pattern else 0).strip()
            # Clean up journal name
            journal = re.sub(r'\s+', ' ', journal).strip()
            metadata['journal'] = journal
            break

    # Extract publication date - look for dates in various formats
    date_patterns = [
        r'(?:published|date|received|accepted)[:;]?\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        r'(?:published|date|received|accepted)[:;]?\s*(\w+ \d{1,2},? \d{4})',
        r'(?:published|date|received|accepted)[:;]?\s*(\w+ \d{4})',
        r'(?:©|\(c\)|\bcopyright\b)(?:\s*\d{4})?[^\d]*(\d{4})'
    ]

    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1).strip()
            # Try to convert to standard format
            try:
                # YYYY-MM-DD or YYYY/MM/DD format
                if re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', date_str):
                    metadata['publication_date'] = date_str.replace('/', '-')
                # Month DD, YYYY format
                elif re.match(r'[A-Za-z]+ \d{1,2},? \d{4}', date_str):
                    month_day_year = re.search(r'([A-Za-z]+) (\d{1,2}),? (\d{4})', date_str)
                    if month_day_year:
                        month = month_day_year.group(1)
                        day = month_day_year.group(2)
                        year = month_day_year.group(3)
                        month_num = {
                            'january': '01', 'february': '02', 'march': '03', 'april': '04',
                            'may': '05', 'june': '06', 'july': '07', 'august': '08',
                            'september': '09', 'october': '10', 'november': '11', 'december': '12'
                        }.get(month.lower(), '01')
                        metadata['publication_date'] = f"{year}-{month_num}-{day.zfill(2)}"
                # Month YYYY format
                elif re.match(r'[A-Za-z]+ \d{4}', date_str):
                    month_year = re.search(r'([A-Za-z]+) (\d{4})', date_str)
                    if month_year:
                        month = month_year.group(1)
                        year = month_year.group(2)
                        month_num = {
                            'january': '01', 'february': '02', 'march': '03', 'april': '04',
                            'may': '05', 'june': '06', 'july': '07', 'august': '08',
                            'september': '09', 'october': '10', 'november': '11', 'december': '12'
                        }.get(month.lower(), '01')
                        metadata['publication_date'] = f"{year}-{month_num}-01"
                # Just year
                elif re.match(r'\d{4}', date_str):
                    metadata['publication_date'] = f"{date_str}-01-01"
            except:
                # If date parsing fails, keep the default
                pass
            break

    return metadata

def process_pdf(pdf_path, use_biobert=True, device=0):
    """
    Process a PDF file through the complete pipeline:
    1. Extract text from PDF
    2. Clean the text
    3. Extract entities and relationships
    4. Store the data in the database

    Args:
        pdf_path (str): Path to the PDF file
        use_biobert (bool): Whether to use BioBERT for entity extraction
        device (int): Device to use for models (-1 for CPU, 0+ for GPU)

    Returns:
        int: The article_id of the processed article
    """
    print(f"Processing PDF: {pdf_path}")

    # Step 1: Extract text from PDF
    parser = PDFParser(remove_linebreaks=True, remove_headers_footers=True)
    cleaner = TextCleaner(lowercase=False, remove_names=False, remove_citations=True)

    print("Extracting and cleaning text...")
    cleaned_text = parser.extract_and_clean_text(pdf_path, cleaner)

    # Step 2: Extract metadata from text
    print("Extracting metadata...")
    metadata = extract_metadata_from_text(cleaned_text)
    metadata['file_path'] = pdf_path
    metadata['processed_text'] = cleaned_text

    # Step 3: Extract entities and relationships
    print("Extracting entities and relationships...")
    extractor = ScientificEntityExtractor(use_biobert=use_biobert, device=device)
    entities = extractor.extract_entities(cleaned_text)
    relationships, aliases = extractor.extract_relationships(cleaned_text)

    # Print summary of extracted information
    print(f"Extracted {sum(len(ents) for ents in entities.values())} entities")
    for category, ents in entities.items():
        print(f"  {category}: {len(ents)}")

    print(f"Extracted {len(relationships)} relationships")
    print(f"Extracted {len(aliases)} aliases")

    # Step 4: Store the data in the database
    print("Storing data in the database...")
    data_store = ScientificDataStore()
    # Ensure database tables exist before storing data
    data_store.create_tables()
    article_id = data_store.process_article_data(metadata, entities, relationships, aliases)

    print(f"Successfully processed article with ID: {article_id}")
    return article_id

def process_directory(directory_path, use_biobert=True, device=0):
    """
    Process all PDF files in a directory.

    Args:
        directory_path (str): Path to the directory containing PDF files
        use_biobert (bool): Whether to use BioBERT for entity extraction
        device (int): Device to use for models (-1 for CPU, 0+ for GPU)

    Returns:
        list: List of article_ids for processed articles
    """
    article_ids = []

    # Ensure the database tables exist
    data_store = ScientificDataStore()
    data_store.create_tables()

    # Process each PDF file in the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            try:
                article_id = process_pdf(pdf_path, use_biobert, device)
                article_ids.append(article_id)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    return article_ids

def main():
    """Main function to run the pipeline from the command line."""
    parser = argparse.ArgumentParser(description='Process scientific articles in PDF format.')
    parser.add_argument('input', help='Path to a PDF file or directory of PDF files')
    parser.add_argument('--no-biobert', action='store_true', help='Disable BioBERT for entity extraction')
    parser.add_argument('--cpu', action='store_true', help='Use CPU instead of GPU')

    args = parser.parse_args()

    # Determine device
    device = -1 if args.cpu else 0

    # Process input
    if os.path.isdir(args.input):
        print(f"Processing directory: {args.input}")
        article_ids = process_directory(args.input, not args.no_biobert, device)
        print(f"Processed {len(article_ids)} articles")
    elif os.path.isfile(args.input) and args.input.lower().endswith('.pdf'):
        print(f"Processing file: {args.input}")
        article_id = process_pdf(args.input, not args.no_biobert, device)
        print(f"Processed article with ID: {article_id}")
    else:
        print("Input must be a PDF file or a directory containing PDF files")

if __name__ == "__main__":
    main()
