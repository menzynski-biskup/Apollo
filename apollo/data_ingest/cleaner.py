# apollo/data_ingest/cleaner.py
import re
import spacy

class TextCleaner:
    def __init__(self, lowercase=True, remove_names=True, remove_citations=True):
        self.lowercase = lowercase
        self.remove_names = remove_names
        self.remove_citations = remove_citations
        self.nlp = spacy.load("en_core_web_lg")  # Use SciSpaCy for more specialized models

    def clean(self, text: str) -> str:
        """Clean up raw text extracted from a PDF."""
        # Step 1: Remove citations if required
        if self.remove_citations:
            text = self.remove_citations_from_text(text)

        # Step 2: Use NER to remove names (if needed)
        if self.remove_names:
            text = self.remove_names_from_text(text)

        # Step 3: Remove unwanted lines (headers/footers, etc.)
        lines = text.splitlines()
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Skip empty lines or obvious footers
            if not line or self.is_footer_or_header(line):
                continue

            # Remove common page markers
            line = re.sub(r"Page\s+\d+(\s+of\s+\d+)?", "", line, flags=re.I)

            cleaned_lines.append(line)

        # Step 4: Join lines and remove multiple spaces
        text = " ".join(cleaned_lines)
        text = re.sub(r"\s{2,}", " ", text)

        # Step 5: Lowercase text if needed
        if self.lowercase:
            text = text.lower()

        return text.strip()

    def remove_citations_from_text(self, text: str) -> str:
        """Remove citation numbers from the text (e.g., (1), 23)."""
        # Adjusted pattern to match citations
        citation_pattern = r"\(\d+\)|\d+\s?"  # Matches (1), 23, (23), etc.
        return re.sub(citation_pattern, "", text)

    def remove_names_from_text(self, text: str) -> str:
        """Remove personal names using NER."""
        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        # Print categorized entities
        for label, ents in entities.items():
            print(f"{label}: {ents}")
        # Use spaCy's NER to find persons and replace them with a placeholder
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                text = text.replace(ent.text, "[NAME]")
        return text

    def is_footer_or_header(self, line: str) -> bool:
        """Check if a line is likely to be a header/footer (heuristic)."""
        keywords = ["journal", "copyright", "doi", "accepted", "received"]
        return any(k in line.lower() for k in keywords)
