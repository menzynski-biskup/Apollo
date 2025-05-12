#!/usr/bin/env python3
"""
Script to load NeuroNames brain region data from JSON into a PostgreSQL database.

This script creates three tables:
1. brain_structures - Core information for each brain region
2. synonyms - Synonyms for each brain region
3. structure_parents - Parent-child relationships between brain regions

The script loads data from the NeuroNames.json file, validates the entries,
and populates the PostgreSQL database accordingly.

Usage:
    python neuronames_to_postgres.py

Requirements:
    - PostgreSQL database server running
    - psycopg2 Python package installed
    - NeuroNames.json file in the specified location

Database Schema:
    - brain_structures:
        - id: Internal primary key
        - neuronames_id: Unique identifier from NeuroNames
        - standard_name: Standard name of the brain region
        - standard_acronym: Standard acronym of the brain region
        - definition: Definition of the brain region
        - brain_info_url: URL to BrainInfo page
        - structure_type: Type of brain structure

    - synonyms:
        - id: Internal primary key
        - brain_structure_id: Foreign key to brain_structures
        - synonym_language: Language of the synonym
        - organism: Organism the synonym applies to
        - synonym_name: Name of the synonym
        - synonym_source: Source of the synonym
        - source_title: Title of the source
        - pubmed_hit_count: Number of PubMed hits for the synonym

    - structure_parents:
        - id: Internal primary key
        - child_id: Foreign key to brain_structures (child)
        - parent_id: Foreign key to brain_structures (parent)
        - hierarchy_model_name: Name of the hierarchy model
        - model_status: Status of the model

Future Extensions:
    This database schema is designed to be extended in the future. Possible extensions include:
    - Adding tables for functions associated with brain regions
    - Adding tables for disorders associated with brain regions
    - Adding tables for gene expression in brain regions
    - Adding tables for connectivity between brain regions

    To extend the database, create new tables with foreign keys to the brain_structures table.
    For example, to add a table for functions:

    CREATE TABLE brain_region_functions (
        id SERIAL PRIMARY KEY,
        brain_structure_id INTEGER REFERENCES brain_structures(id),
        function_name TEXT,
        function_description TEXT,
        evidence_level TEXT,
        reference TEXT
    );
"""

import json
import psycopg2
from psycopg2.extras import execute_values
import os
import sys
from pathlib import Path

# Database connection parameters - edit
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432"
}

# Path to the NeuroNames JSON file
NEURONAMES_JSON_PATH = Path("/brain_regions/json/NeuroNames.json") #Edit to right path for your .json file

def create_tables(conn):
    """
    Create the necessary tables in the PostgreSQL database if they don't exist.

    Args:
        conn: PostgreSQL database connection
    """
    cursor = conn.cursor()

    # Create brain_structures table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brain_structures (
        id SERIAL PRIMARY KEY,
        neuronames_id VARCHAR(50) UNIQUE NOT NULL,
        standard_name TEXT,
        standard_acronym TEXT,
        definition TEXT,
        brain_info_url TEXT,
        structure_type TEXT
    );
    """)

    # Create synonyms table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS synonyms (
        id SERIAL PRIMARY KEY,
        brain_structure_id INTEGER REFERENCES brain_structures(id),
        synonym_language TEXT,
        organism TEXT,
        synonym_name TEXT NOT NULL,
        synonym_source TEXT,
        source_title TEXT,
        pubmed_hit_count INTEGER
    );
    """)

    # Create structure_parents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS structure_parents (
        id SERIAL PRIMARY KEY,
        child_id INTEGER REFERENCES brain_structures(id),
        parent_id INTEGER REFERENCES brain_structures(id),
        hierarchy_model_name TEXT,
        model_status TEXT
    );
    """)

    conn.commit()
    cursor.close()

def load_json_data(json_path):
    """
    Load and parse the NeuroNames JSON file.

    Args:
        json_path: Path to the NeuroNames JSON file

    Returns:
        List of brain region entries from the JSON file
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} brain region entries from {json_path}")
        return data
    except Exception as e:
        print(f"Error loading JSON file: {str(e)}")
        sys.exit(1)

def insert_brain_structures(conn, data):
    """
    Insert brain structures into the brain_structures table.

    Args:
        conn: PostgreSQL database connection
        data: List of brain region entries from the JSON file

    Returns:
        Dictionary mapping neuroNamesID to internal primary key (id)
    """
    cursor = conn.cursor()

    # Prepare data for insertion
    structures = []
    for entry in data:
        structures.append((
            entry.get('neuroNamesID', ''),
            entry.get('standardName', ''),
            entry.get('standardAcronym', ''),
            entry.get('cDefinition', ''),
            entry.get('brainInfoURL', ''),
            entry.get('brainStructureType', '')
        ))

    # Insert data into brain_structures table
    execute_values(
        cursor,
        """
        INSERT INTO brain_structures 
        (neuronames_id, standard_name, standard_acronym, definition, brain_info_url, structure_type)
        VALUES %s
        ON CONFLICT (neuronames_id) DO UPDATE SET
            standard_name = EXCLUDED.standard_name,
            standard_acronym = EXCLUDED.standard_acronym,
            definition = EXCLUDED.definition,
            brain_info_url = EXCLUDED.brain_info_url,
            structure_type = EXCLUDED.structure_type
        RETURNING id, neuronames_id
        """,
        structures
    )

    # Create mapping from neuroNamesID to internal primary key (id)
    id_mapping = {}
    for row in cursor.fetchall():
        id_mapping[row[1]] = row[0]  # Map neuronames_id to id

    conn.commit()
    print(f"Inserted {len(structures)} brain structures into the database")

    # If some entries weren't inserted, create a mapping for them
    if len(id_mapping) < len(structures):
        cursor.execute("SELECT id, neuronames_id FROM brain_structures")
        for row in cursor.fetchall():
            id_mapping[row[1]] = row[0]

    cursor.close()
    return id_mapping

def insert_structure_parents(conn, data, id_mapping):
    """
    Insert parent-child relationships into the structure_parents table.

    Args:
        conn: PostgreSQL database connection
        data: List of brain region entries from the JSON file
        id_mapping: Dictionary mapping neuroNamesID to internal primary key (id)
    """
    cursor = conn.cursor()

    # Prepare data for insertion
    parent_relationships = []
    missing_parents = {}

    for entry in data:
        child_id = id_mapping.get(entry.get('neuroNamesID', ''))
        if not child_id:
            continue

        parents = entry.get('parents', [])
        for parent in parents:
            parent_neuronames_id = parent.get('parentNeuroNamesId', '')
            parent_id = id_mapping.get(parent_neuronames_id)
            if not parent_id:
                # Track missing parents
                if parent_neuronames_id not in missing_parents:
                    missing_parents[parent_neuronames_id] = {
                        'count': 0,
                        'name': parent.get('parentStandardName', 'Unknown'),
                        'model': parent.get('modelName', 'Unknown')
                    }
                missing_parents[parent_neuronames_id]['count'] += 1
                continue

            parent_relationships.append((
                child_id,
                parent_id,
                parent.get('modelName', ''),
                parent.get('modelStatus', '')
            ))

    # Insert data into structure_parents table
    if parent_relationships:
        execute_values(
            cursor,
            """
            INSERT INTO structure_parents 
            (child_id, parent_id, hierarchy_model_name, model_status)
            VALUES %s
            ON CONFLICT DO NOTHING
            """,
            parent_relationships
        )

        conn.commit()
        print(f"Inserted {len(parent_relationships)} parent-child relationships into the database")
    else:
        print("No parent-child relationships found")

    # Print summary of missing parents
    if missing_parents:
        print(f"\nSummary of missing parent structures ({len(missing_parents)} unique IDs):")
        print("NeuroNamesID | Count | Name | Model")
        print("-" * 80)
        for parent_id, info in sorted(missing_parents.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
            print(f"{parent_id} | {info['count']} | {info['name']} | {info['model']}")

        if len(missing_parents) > 10:
            print(f"... and {len(missing_parents) - 10} more")

    cursor.close()

def insert_synonyms(conn, data, id_mapping):
    """
    Insert synonyms into the synonyms table.

    Args:
        conn: PostgreSQL database connection
        data: List of brain region entries from the JSON file
        id_mapping: Dictionary mapping neuroNamesID to internal primary key (id)
    """
    cursor = conn.cursor()

    # Prepare data for insertion
    all_synonyms = []
    for entry in data:
        brain_structure_id = id_mapping.get(entry.get('neuroNamesID', ''))
        if not brain_structure_id:
            continue

        synonyms = entry.get('synonyms', [])
        for synonym in synonyms:
            all_synonyms.append((
                brain_structure_id,
                synonym.get('synonymLanguage', ''),
                synonym.get('organism', ''),
                synonym.get('synonymName', ''),
                synonym.get('synonymSource', ''),
                synonym.get('synonymSourceTitle', ''),
                int(synonym.get('pubMedHits', '0')) if synonym.get('pubMedHits', '').isdigit() else 0
            ))

    # Insert data into synonyms table
    if all_synonyms:
        execute_values(
            cursor,
            """
            INSERT INTO synonyms 
            (brain_structure_id, synonym_language, organism, synonym_name, synonym_source, source_title, pubmed_hit_count)
            VALUES %s
            ON CONFLICT DO NOTHING
            """,
            all_synonyms
        )

        conn.commit()
        print(f"Inserted {len(all_synonyms)} synonyms into the database")
    else:
        print("No synonyms found")

    cursor.close()

def main():
    """
    Main function to load NeuroNames data into PostgreSQL database.
    """
    # Check if the JSON file exists
    if not NEURONAMES_JSON_PATH.exists():
        print(f"Error: NeuroNames JSON file not found at {NEURONAMES_JSON_PATH}")
        sys.exit(1)

    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_PARAMS)

        # Create tables if they don't exist
        create_tables(conn)

        # Load JSON data
        data = load_json_data(NEURONAMES_JSON_PATH)

        # Insert brain structures and get id mapping
        id_mapping = insert_brain_structures(conn, data)

        # Insert parent-child relationships
        insert_structure_parents(conn, data, id_mapping)

        # Insert synonyms
        insert_synonyms(conn, data, id_mapping)

        # Close database connection
        conn.close()

        print("Successfully loaded NeuroNames data into PostgreSQL database")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
