# Apollo - Scientific Article Analysis Pipeline

Apollo is a comprehensive pipeline for extracting, analyzing, and storing information from scientific articles in PDF format. It extracts plain text from PDFs, identifies key terms and relationships, and stores them in a structured database for later retrieval and summarization.

## Features

- **PDF Text Extraction**: Extracts text from scientific PDFs while removing headers, footers, and handling hyphenated words
- **Metadata Extraction**: Intelligently identifies article titles, authors, journal names, and publication dates
- **Entity Recognition**: Identifies key scientific terms like diseases, biomarkers, symptoms, proteins, brain regions, etc.
- **Predefined Entity Lists**: Uses predefined lists of diseases, symptoms, proteins, brain regions, and acronyms for improved entity recognition
- **Alias Detection**: Automatically detects aliases (e.g., "Alzheimer's disease (AD)" identifies AD as an alias)
- **Relationship Extraction**: Identifies relationships between scientific entities
- **Database Storage**: Stores all extracted information in a PostgreSQL database with proper citations
- **Brain Atlas Integration**: Imports comprehensive brain atlas data from multiple sources (EBRAINS, NeuroNames, Allen Brain Atlas, AAL Atlas)
- **Command-line Interface**: Easy-to-use CLI for processing individual PDFs or entire directories

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/apollo.git
   cd apollo
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the PostgreSQL database:
   - Install PostgreSQL if not already installed
   - Create a database named "postgres" (or update the connection string in the code)
   - Update the database credentials in `apollo/data_storage/scientific_data_store.py` if needed
   - Run the database setup script to create tables and populate predefined entity lists:
     ```
     python -m apollo.cognitive_atlas_import.setup_database
     ```
   - (Optional) Set up the brain atlas database schema:
     ```
     python -m apollo.brain_atlas_import.brain_atlas_schema
     ```

4. Download required models:
   ```
   python -m spacy download en_core_web_lg
   ```

5. (Optional) Docker setup:
   - Install Docker and Docker Compose
   - Run the application with PostgreSQL using Docker Compose:
     ```
     docker-compose up
     ```

## Usage

### Command Line Interface

Process a single PDF file:
```
python -m apollo.main /path/to/your/article.pdf
```

Process all PDFs in a directory:
```
python -m apollo.main /path/to/your/pdf/directory
```

Options:
- `--no-biobert`: Disable BioBERT for entity extraction (faster but less accurate)
- `--cpu`: Use CPU instead of GPU for model inference

### Python API

```python
from apollo.main import process_pdf

# Process a single PDF
article_id = process_pdf('/path/to/your/article.pdf')
```

### Brain Atlas Import

Import brain atlas data from various sources:
```
python -m apollo.brain_atlas_import.ingestion
```

Options:
- `--connection`: PostgreSQL connection string
- `--output-dir`: Directory to save extracted data as JSON
- `--json-file`: Path to a JSON file to ingest

Import NeuroNames brain region data from JSON into PostgreSQL:
```
python -m apollo.neuronames_to_postgres
```

This script creates three tables:
1. `brain_structures`: Core information for each brain region
2. `synonyms`: Synonyms for each brain region
3. `structure_parents`: Parent-child relationships between brain regions

The script loads data from the NeuroNames.json file, validates the entries, and populates the PostgreSQL database accordingly.

Validate brain atlas data:
```
python -m apollo.brain_atlas_import.validation /path/to/data.json
```

Generate graph database schemas:
```
python -m apollo.brain_atlas_import.graph_schema --neptune --neo4j --example
```

## Project Structure

- `apollo/data_ingest/`: PDF parsing and text cleaning
  - `pdf_parser.py`: Extracts text from PDFs
  - `cleaner.py`: Cleans and preprocesses text
- `apollo/ner/`: Named Entity Recognition
  - `extractor.py`: Base BioBERT entity extractor
  - `scientific_extractor.py`: Scientific entity and relationship extractor
- `apollo/data_storage/`: Database storage
  - `scientific_data_store.py`: Stores entities, relationships, and citations
- `apollo/cognitive_atlas_import/`: Database setup and predefined entity lists
  - `setup_database.py`: Main script to run all database setup scripts
  - `diseases_to_psql.py`: Imports diseases from Cognitive Atlas API
  - `symptoms_to_psql.py`: Imports symptoms for neurodegenerative diseases
  - `proteins_to_psql.py`: Imports proteins relevant to neurodegenerative diseases
  - `brain_regions_to_psql.py`: Imports brain regions relevant to neurodegenerative diseases
  - `acronyms_to_psql.py`: Imports common acronyms used in neuroscience
- `apollo/brain_atlas_import/`: Comprehensive brain atlas data import
  - `brain_atlas_schema.py`: Defines the PostgreSQL schema for brain atlas data
  - `json_schemas.py`: Defines JSON schemas for validating brain atlas data
  - `ingestion.py`: Main script for ingesting brain atlas data into PostgreSQL
  - `validation.py`: Validates brain atlas data against schemas and checks consistency
  - `graph_schema.py`: Defines graph database schemas for Amazon Neptune and Neo4j
  - `extractors/`: Modules for extracting data from various sources
    - `ebrains_extractor.py`: Extracts data from EBRAINS Knowledge Graph API
    - `neuronames_extractor.py`: Extracts data from NeuroNames via web scraping
    - `allen_brain_atlas_extractor.py`: Extracts data from Allen Brain Atlas API
    - `aal_atlas_extractor.py`: Extracts data from AAL Atlas CSV/XML files
- `apollo/main.py`: Main pipeline script

## Database Schema

### Core Tables
- `articles`: Stores article metadata and processed text
- `scientific_entities`: Stores extracted entities with their type and context
- `entity_aliases`: Stores aliases for entities (e.g., "AD" for "Alzheimer's disease")
- `entity_relationships`: Stores relationships between entities
- `entity_citations`: Links entities to the articles they appear in
- `relationship_citations`: Links relationships to the articles they appear in

### Predefined Entity Lists
- `diseases`: Predefined list of diseases and disorders
- `symptoms`: Predefined list of symptoms and clinical signs
- `proteins`: Predefined list of proteins and biomarkers
- `brain_regions`: Predefined list of brain regions and structures
- `acronyms`: Predefined list of acronyms and their full forms

### Brain Atlas Tables
- `data_sources`: Information about brain atlas data sources
- `brain_regions`: Comprehensive brain region data from multiple sources
- `region_aliases`: Alternative names for brain regions
- `region_hierarchy`: Parent-child relationships between brain regions
- `region_relationships`: Other types of relationships between brain regions
- `region_functions`: Functions of brain regions
- `import_logs`: Logs of brain atlas import operations

## Example

Given a scientific article with text like:
```
It is necessary to separate syndrome (clinically identified impairment) from biology (etiology). 
Alzheimer's disease (AD) is defined by its biology with the following implications. 
AD is defined by its unique neuropathologic findings; therefore, detection of AD neuropathologic 
change by biomarkers is equivalent to diagnosing the disease. Tau and p-tau are important 
biomarkers found in the hippocampus and temporal lobe regions.
```

Apollo will extract:
- Entities: 
  - "Alzheimer's disease" (DISEASE)
  - "syndrome" (SYNDROME)
  - "biomarkers" (BIOMARKER)
  - "tau" (PROTEIN)
  - "p-tau" (PROTEIN)
  - "hippocampus" (BRAIN_REGION)
  - "temporal lobe" (BRAIN_REGION)
  - "neuropathologic findings" (NEUROPATHOLOGIC)
- Aliases: "AD" for "Alzheimer's disease"
- Relationships: 
  - "Alzheimer's disease HAS_BIOMARKER biomarkers"
  - "tau IS_A biomarker"
  - "p-tau IS_A biomarker"
  - "tau FOUND_IN hippocampus"
  - "p-tau FOUND_IN temporal lobe"

This information is stored in the database with proper citations to the source article, allowing for later retrieval and summarization. The use of predefined entity lists ensures that entities like "p-tau" are correctly classified as proteins rather than being misclassified as person names.
