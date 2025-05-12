# apollo/ner/extractor.py

from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import torch

class BioBERTNER:
    def __init__(self, model_name="dmis-lab/biobert-v1.1", device=0):
        """
        Initializes BioBERTNER with BioBERT model and tokenizer.

        Args:
            model_name (str): HuggingFace model name (default is BioBERT v1.1).
            device (int): The device to use for inference (0 for GPU, -1 for CPU).
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.device = device
        self.ner_pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer, device=self.device)

    def extract_entities(self, text: str):
        """
        Extracts named entities from input text using BioBERT.

        Args:
            text (str): The input text to extract entities from.

        Returns:
            List of entities extracted, including their label and score.
        """
        entities = self.ner_pipeline(text)
        print(entities)  # Print the raw output to see its structure
        return entities

    def categorize_entities(self, entities):
        """
        Categorizes entities into a dictionary by their label.

        Args:
            entities (list): List of entities extracted from the text.

        Returns:
            dict: Categorized entities by their labels.
        """
        categorized = {}
        for entity in entities:
            print(f"Entity: {entity}")  # Check each entity in the list
            label = entity.get('entity', 'Unknown')  # Updated to match the correct key
            if label not in categorized:
                categorized[label] = []
            categorized[label].append(entity['word'])
        return categorized


# Example Usage:
if __name__ == "__main__":
    # Sample input text (from PDF or other source)
    text = """
    Amyloidosis is a disease that results from the deposition of amyloid proteins in tissues and organs.
    Patients may experience symptoms such as fatigue and swelling. 
    """

    # Initialize BioBERTNER
    bio_bert_ner = BioBERTNER()

    # Extract entities from text
    entities = bio_bert_ner.extract_entities(text)

    # Categorize the entities
    categorized_entities = bio_bert_ner.categorize_entities(entities)

    # Print categorized entities
    for label, ents in categorized_entities.items():
        print(f"{label}: {ents}")