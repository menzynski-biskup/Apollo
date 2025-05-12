# apollo/ner/scientific_extractor.py

import spacy
from spacy.tokens import Doc, Span
from spacy.language import Language
from transformers import pipeline
from apollo.ner.extractor import BioBERTNER
import re

class ScientificEntityExtractor:
    """
    A class for extracting scientific entities and relationships from text.
    Combines BioBERT NER with custom rules for scientific terms and relationships.
    """

    def __init__(self, use_biobert=True, device=0, use_predefined_entities=True):
        """
        Initialize the scientific entity extractor.

        Args:
            use_biobert (bool): Whether to use BioBERT for biomedical entity extraction
            device (int): Device to use for BioBERT (-1 for CPU, 0+ for GPU)
            use_predefined_entities (bool): Whether to use predefined entity lists from the database
        """
        # Load spaCy model for general NLP tasks
        self.nlp = spacy.load("en_core_web_lg")

        # Flag for using predefined entities
        self.use_predefined_entities = use_predefined_entities

        # Load predefined entity lists from database if requested
        self.predefined_diseases = {}
        self.predefined_symptoms = {}
        self.predefined_proteins = {}
        self.predefined_brain_regions = {}
        self.predefined_acronyms = {}

        if use_predefined_entities:
            self._load_predefined_entities()

        # Add custom components to the pipeline
        if not Language.has_factory("scientific_term_ruler"):
            Language.factory("scientific_term_ruler", func=self._create_scientific_term_ruler)

        if "scientific_term_ruler" not in self.nlp.pipe_names:
            self.nlp.add_pipe("scientific_term_ruler")

        # Initialize BioBERT NER if requested
        self.use_biobert = use_biobert
        if use_biobert:
            self.biobert_ner = BioBERTNER(device=device)

        # Initialize relationship extraction pipeline
        try:
            # Try to use the specific relation extraction model
            self.relation_extractor = pipeline(
                "text-classification",
                model="allenai/scibert_scivocab_uncased_finetuned_relation_extraction",
                device=device if device >= 0 else -1
            )
        except Exception as e:
            print(f"Warning: Could not load specific relation extraction model: {str(e)}")
            print("Using general-purpose SciBERT model instead.")
            # Fallback to a general-purpose SciBERT model
            self.relation_extractor = pipeline(
                "text-classification",
                model="allenai/scibert_scivocab_uncased",
                device=device if device >= 0 else -1
            )

    def _load_predefined_entities(self):
        """
        Load predefined entity lists from the database.
        This includes diseases, symptoms, proteins, brain regions, and acronyms.
        """
        try:
            import psycopg2

            # Connect to the database
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="Radek1994",
                host="localhost",
                port="5432"
            )

            cursor = conn.cursor()

            # Load diseases
            try:
                cursor.execute("SELECT name, definition FROM diseases")
                for row in cursor.fetchall():
                    name, definition = row
                    if name and len(name) > 1:
                        self.predefined_diseases[name] = definition or ""
            except Exception as e:
                print(f"Warning: Could not load diseases from database: {str(e)}")

            # Load symptoms (if table exists)
            try:
                cursor.execute("SELECT name, definition FROM symptoms")
                for row in cursor.fetchall():
                    name, definition = row
                    if name and len(name) > 1:
                        self.predefined_symptoms[name] = definition or ""
            except Exception as e:
                print(f"Warning: Could not load symptoms from database: {str(e)}")

            # Load proteins (if table exists)
            try:
                cursor.execute("SELECT name, description FROM proteins")
                for row in cursor.fetchall():
                    name, description = row
                    if name and len(name) > 1:
                        self.predefined_proteins[name] = description or ""
            except Exception as e:
                print(f"Warning: Could not load proteins from database: {str(e)}")

            # Load brain regions (if table exists)
            try:
                cursor.execute("SELECT name, description FROM brain_regions")
                for row in cursor.fetchall():
                    name, description = row
                    if name and len(name) > 1:
                        self.predefined_brain_regions[name] = description or ""
            except Exception as e:
                print(f"Warning: Could not load brain regions from database: {str(e)}")

            # Load acronyms (if table exists)
            try:
                cursor.execute("SELECT acronym, full_form FROM acronyms")
                for row in cursor.fetchall():
                    acronym, full_form = row
                    if acronym and full_form and len(acronym) > 1:
                        self.predefined_acronyms[acronym] = full_form
            except Exception as e:
                print(f"Warning: Could not load acronyms from database: {str(e)}")

            # Close database connection
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Warning: Could not connect to database to load predefined entities: {str(e)}")
            print("Continuing without predefined entity lists.")

    def _create_scientific_term_ruler(self, nlp, name):
        """Create a custom entity ruler for scientific terms."""
        from spacy.pipeline import EntityRuler
        ruler = EntityRuler(nlp, overwrite_ents=False)

        # Add patterns for common scientific terms
        patterns = [
            {"label": "DISEASE", "pattern": [{"LOWER": "alzheimer"}, {"LOWER": "'s"}, {"LOWER": "disease"}]},
            {"label": "DISEASE", "pattern": [{"LOWER": "alzheimer"}, {"LOWER": "disease"}]},
            {"label": "DISEASE", "pattern": [{"LOWER": "ad"}]},  # Common abbreviation for Alzheimer's disease
            {"label": "BIOMARKER", "pattern": [{"LOWER": "biomarker"}]},
            {"label": "BIOMARKER", "pattern": [{"LOWER": "core"}, {"LOWER": "biomarker"}]},
            {"label": "SYMPTOM", "pattern": [{"LOWER": "symptom"}]},
            {"label": "SYMPTOM", "pattern": [{"LOWER": "symptoms"}]},
            {"label": "SYNDROME", "pattern": [{"LOWER": "syndrome"}]},
            {"label": "ETIOLOGY", "pattern": [{"LOWER": "etiology"}]},
            {"label": "NEUROPATHOLOGIC", "pattern": [{"LOWER": "neuropathologic"}]},
            {"label": "NEUROPATHOLOGIC", "pattern": [{"LOWER": "neuropathologic"}, {"LOWER": "change"}]},
            {"label": "NEUROPATHOLOGIC", "pattern": [{"LOWER": "neuropathologic"}, {"LOWER": "finding"}]},
            # Common protein markers in neurodegenerative diseases
            {"label": "PROTEIN", "pattern": [{"LOWER": "tau"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "p-tau"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "phosphorylated"}, {"LOWER": "tau"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "amyloid"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "amyloid"}, {"LOWER": "beta"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "aβ"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "alpha-synuclein"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "α-synuclein"}]},
            {"label": "PROTEIN", "pattern": [{"LOWER": "tdp-43"}]},
            # Common brain regions
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "hippocampus"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "hippocampal"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "frontal"}, {"LOWER": "lobe"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "temporal"}, {"LOWER": "lobe"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "parietal"}, {"LOWER": "lobe"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "occipital"}, {"LOWER": "lobe"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "amygdala"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "cerebellum"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "basal"}, {"LOWER": "ganglia"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "thalamus"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "hypothalamus"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "brainstem"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "cortex"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "prefrontal"}, {"LOWER": "cortex"}]},
            {"label": "BRAIN_REGION", "pattern": [{"LOWER": "entorhinal"}, {"LOWER": "cortex"}]},
            # Cognitive processes and functions
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "memory"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "working"}, {"LOWER": "memory"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "episodic"}, {"LOWER": "memory"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "semantic"}, {"LOWER": "memory"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "attention"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "executive"}, {"LOWER": "function"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "language"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "visuospatial"}]},
            {"label": "COGNITIVE_PROCESS", "pattern": [{"LOWER": "processing"}, {"LOWER": "speed"}]},
        ]

        # Add patterns from predefined entity lists if available
        if hasattr(self, 'use_predefined_entities') and self.use_predefined_entities:
            # Add disease patterns
            for disease_name in self.predefined_diseases:
                if len(disease_name.split()) > 1:
                    # Multi-word disease name
                    pattern = {"label": "DISEASE", "pattern": [{"LOWER": word.lower()} for word in disease_name.split()]}
                    patterns.append(pattern)
                else:
                    # Single-word disease name
                    pattern = {"label": "DISEASE", "pattern": [{"LOWER": disease_name.lower()}]}
                    patterns.append(pattern)

            # Add symptom patterns
            for symptom_name in self.predefined_symptoms:
                if len(symptom_name.split()) > 1:
                    # Multi-word symptom name
                    pattern = {"label": "SYMPTOM", "pattern": [{"LOWER": word.lower()} for word in symptom_name.split()]}
                    patterns.append(pattern)
                else:
                    # Single-word symptom name
                    pattern = {"label": "SYMPTOM", "pattern": [{"LOWER": symptom_name.lower()}]}
                    patterns.append(pattern)

            # Add protein patterns
            for protein_name in self.predefined_proteins:
                if len(protein_name.split()) > 1:
                    # Multi-word protein name
                    pattern = {"label": "PROTEIN", "pattern": [{"LOWER": word.lower()} for word in protein_name.split()]}
                    patterns.append(pattern)
                else:
                    # Single-word protein name
                    pattern = {"label": "PROTEIN", "pattern": [{"LOWER": protein_name.lower()}]}
                    patterns.append(pattern)

            # Add brain region patterns
            for region_name in self.predefined_brain_regions:
                if len(region_name.split()) > 1:
                    # Multi-word brain region name
                    pattern = {"label": "BRAIN_REGION", "pattern": [{"LOWER": word.lower()} for word in region_name.split()]}
                    patterns.append(pattern)
                else:
                    # Single-word brain region name
                    pattern = {"label": "BRAIN_REGION", "pattern": [{"LOWER": region_name.lower()}]}
                    patterns.append(pattern)

            # Add acronym patterns
            for acronym, full_form in self.predefined_acronyms.items():
                # Determine entity type based on full form
                entity_type = "ACRONYM"
                if any(disease in full_form.lower() for disease in ["disease", "disorder", "syndrome"]):
                    entity_type = "DISEASE"
                elif any(symptom in full_form.lower() for symptom in ["symptom", "sign", "deficit"]):
                    entity_type = "SYMPTOM"
                elif any(protein in full_form.lower() for protein in ["protein", "peptide", "enzyme"]):
                    entity_type = "PROTEIN"
                elif any(region in full_form.lower() for region in ["cortex", "lobe", "brain", "nucleus"]):
                    entity_type = "BRAIN_REGION"

                # Add pattern for the acronym
                pattern = {"label": entity_type, "pattern": [{"LOWER": acronym.lower()}]}
                patterns.append(pattern)

        ruler.add_patterns(patterns)
        return ruler

    def extract_entities(self, text):
        """
        Extract scientific entities from text.

        Args:
            text (str): The text to extract entities from

        Returns:
            dict: Dictionary of entities by category
        """
        # Process with spaCy
        doc = self.nlp(text)

        # Extract entities from spaCy
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []

            # Store entity with context
            entity_info = {
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "context": text[max(0, ent.start_char - 50):min(len(text), ent.end_char + 50)]
            }

            # Check if this entity is already in the list
            if not any(e["text"].lower() == ent.text.lower() for e in entities[ent.label_]):
                entities[ent.label_].append(entity_info)

        # If using BioBERT, add its entities
        if self.use_biobert:
            biobert_entities = self.biobert_ner.extract_entities(text)
            categorized = self.biobert_ner.categorize_entities(biobert_entities)

            for label, ents in categorized.items():
                if label not in entities:
                    entities[label] = []

                for ent in ents:
                    # Check if this entity is already in the list
                    if not any(e["text"].lower() == ent.lower() for e in entities[label]):
                        # Find the entity in the original text to get context
                        match = re.search(r'\b' + re.escape(ent) + r'\b', text)
                        if match:
                            start, end = match.span()
                            entity_info = {
                                "text": ent,
                                "start": start,
                                "end": end,
                                "context": text[max(0, start - 50):min(len(text), end + 50)]
                            }
                            entities[label].append(entity_info)

        return entities

    def extract_aliases(self, text):
        """
        Extract aliases from text (e.g., "Alzheimer's disease (AD)" identifies AD as an alias).

        Args:
            text (str): The text to extract aliases from

        Returns:
            dict: Dictionary mapping terms to their aliases
        """
        aliases = {}

        # Pattern for finding aliases in parentheses
        alias_pattern = r'([A-Za-z\s\'-]+)\s*\(([A-Z]{1,5})\)'

        for match in re.finditer(alias_pattern, text):
            term = match.group(1).strip()
            alias = match.group(2).strip()
            aliases[term] = alias

        return aliases

    def extract_relationships(self, text):
        """
        Extract relationships between entities in the text.

        Args:
            text (str): The text to extract relationships from

        Returns:
            list: List of relationship dictionaries
        """
        # Process with spaCy to get entities
        doc = self.nlp(text)

        # Extract aliases first
        aliases = self.extract_aliases(text)

        # Get all entities
        entities = self.extract_entities(text)

        # Flatten entities list
        all_entities = []
        for category, ents in entities.items():
            for ent in ents:
                all_entities.append((ent["text"], ent["start"], ent["end"], category))

        # Sort entities by position in text
        all_entities.sort(key=lambda x: x[1])

        # Extract relationships between nearby entities
        relationships = []

        # For each pair of entities within a reasonable distance
        for i in range(len(all_entities)):
            for j in range(i+1, len(all_entities)):
                entity1 = all_entities[i]
                entity2 = all_entities[j]

                # Skip if entities are too far apart (more than 200 chars)
                if entity2[1] - entity1[2] > 200:
                    continue

                # Extract the text between the two entities
                between_text = text[entity1[2]:entity2[1]]

                # Create a sample for the relation extractor
                sample = f"{entity1[0]} [SEP] {between_text} [SEP] {entity2[0]}"

                # Use the relation extractor to classify the relationship
                relation_result = self.relation_extractor(sample)

                # Add to relationships if confidence is high enough
                if relation_result[0]["score"] > 0.7:
                    relationship = {
                        "entity1": entity1[0],
                        "entity1_type": entity1[3],
                        "entity2": entity2[0],
                        "entity2_type": entity2[3],
                        "relation": relation_result[0]["label"],
                        "confidence": relation_result[0]["score"],
                        "context": text[max(0, entity1[1] - 20):min(len(text), entity2[2] + 20)]
                    }
                    relationships.append(relationship)

        return relationships, aliases

# Example usage
if __name__ == "__main__":
    extractor = ScientificEntityExtractor()

    text = """
    It is necessary to separate syndrome (clinically identified impairment) from biology (etiology). 
    Alzheimer's disease (AD) is defined by its biology with the following implications. 
    AD is defined by its unique neuropathologic findings; therefore, detection of AD neuropathologic 
    change by biomarkers is equivalent to diagnosing the disease.
    """

    entities = extractor.extract_entities(text)
    relationships, aliases = extractor.extract_relationships(text)

    print("Entities:")
    for category, ents in entities.items():
        print(f"  {category}:")
        for ent in ents:
            print(f"    - {ent['text']}")

    print("\nAliases:")
    for term, alias in aliases.items():
        print(f"  {term} -> {alias}")

    print("\nRelationships:")
    for rel in relationships:
        print(f"  {rel['entity1']} ({rel['entity1_type']}) {rel['relation']} {rel['entity2']} ({rel['entity2_type']})")
        print(f"    Context: {rel['context']}")
