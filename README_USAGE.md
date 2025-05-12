# How to Run Apollo and Verify It's Working

This guide will walk you through the steps to run the Apollo scientific article analysis pipeline and verify that it's working correctly.

## Prerequisites

Before running Apollo, make sure you have:

1. Installed all dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Downloaded the required spaCy model:
   ```
   python -m spacy download en_core_web_lg
   ```

3. Set up a PostgreSQL database:
   - Install PostgreSQL if not already installed
   - Create a database named "postgres" (or update the connection string in the code)
   - Update the database credentials in `apollo/data_storage/scientific_data_store.py` if needed
   - The necessary database tables will be created automatically when running the script

## Running Apollo

### Processing a Single PDF

To process a single PDF file:

```bash
python -m apollo.main data/sample.pdf
```

This will:
1. Extract text from the PDF
2. Clean the text
3. Extract entities and relationships
4. Store the data in the database

### Processing Multiple PDFs

To process all PDFs in a directory:

```bash
python -m apollo.main data
```

### Command-Line Options

Apollo supports the following command-line options:

- `--no-biobert`: Disable BioBERT for entity extraction (faster but less accurate)
- `--cpu`: Use CPU instead of GPU for model inference (use this if you don't have a GPU)

Example:
```bash
python -m apollo.main data/sample.pdf --cpu --no-biobert
```

## Verifying That Apollo Is Working

### Expected Output

When running Apollo, you should see output similar to the following:

```
Processing PDF: data/sample.pdf
Extracting and cleaning text...
Extracting metadata...
Extracting entities and relationships...
Extracted X entities
  DISEASE: Y
  BIOMARKER: Z
  ...
Extracted N relationships
Extracted M aliases
Storing data in the database...
Successfully processed article with ID: 1
```

### Checking the Database

To verify that data was correctly stored in the database, you can use a PostgreSQL client to query the database:

```sql
-- Check articles table
SELECT * FROM articles;

-- Check entities
SELECT * FROM scientific_entities;

-- Check relationships
SELECT * FROM entity_relationships;

-- Check aliases
SELECT * FROM entity_aliases;
```

### Common Issues and Troubleshooting

1. **Database Connection Issues**:
   - Verify your PostgreSQL credentials in `apollo/data_storage/scientific_data_store.py`
   - Make sure PostgreSQL is running
   - If you see an error like "relation 'articles' does not exist", it means the database tables haven't been created. This should happen automatically, but if it doesn't, you can manually create them by running:
     ```python
     from apollo.data_storage.scientific_data_store import ScientificDataStore
     data_store = ScientificDataStore()
     data_store.create_tables()
     ```

2. **Model Loading Issues**:
   - If you see errors related to loading models, make sure you've downloaded all required models
   - Try running with `--no-biobert --cpu` flags to use simpler models

3. **PDF Parsing Issues**:
   - If you encounter errors with specific PDFs, try with different sample PDFs
   - Some PDFs may have security features that prevent text extraction

## Example Workflow

Here's a complete example workflow:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_lg
   ```

2. Set up PostgreSQL database (if not already done)

3. Process a sample PDF:
   ```bash
   python -m apollo.main data/sample.pdf --cpu
   ```

4. Verify the output in the terminal

5. Check the database to see if entities and relationships were stored

## Using the Python API

You can also use Apollo programmatically in your Python code:

```python
from apollo.main import process_pdf

# Process a single PDF
article_id = process_pdf('data/sample.pdf', use_biobert=False, device=-1)  # CPU mode
print(f"Processed article with ID: {article_id}")
```

This allows you to integrate Apollo into your own applications or workflows.
