import psycopg2
import requests
from datetime import datetime

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# Create the table for proteins if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS proteins (
        protein_id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        category VARCHAR,
        is_biomarker BOOLEAN DEFAULT FALSE
    );
""")
conn.commit()

# Define a list of common proteins in neurodegenerative diseases
proteins = [
    {
        "name": "Tau",
        "description": "A protein that stabilizes microtubules. Abnormal tau is associated with Alzheimer's disease and other tauopathies.",
        "category": "Microtubule-associated",
        "is_biomarker": True
    },
    {
        "name": "p-tau",
        "description": "Phosphorylated tau protein, a biomarker for Alzheimer's disease and other tauopathies.",
        "category": "Microtubule-associated",
        "is_biomarker": True
    },
    {
        "name": "Amyloid beta",
        "description": "A peptide of 36–43 amino acids that is the main component of amyloid plaques found in Alzheimer's disease.",
        "category": "Amyloid",
        "is_biomarker": True
    },
    {
        "name": "Aβ",
        "description": "Abbreviation for Amyloid beta, a peptide involved in Alzheimer's disease.",
        "category": "Amyloid",
        "is_biomarker": True
    },
    {
        "name": "Alpha-synuclein",
        "description": "A protein that is the main component of Lewy bodies, found in Parkinson's disease and Lewy body dementia.",
        "category": "Synuclein",
        "is_biomarker": True
    },
    {
        "name": "α-synuclein",
        "description": "Abbreviation for Alpha-synuclein, a protein involved in Parkinson's disease.",
        "category": "Synuclein",
        "is_biomarker": True
    },
    {
        "name": "TDP-43",
        "description": "TAR DNA-binding protein 43, a protein involved in frontotemporal dementia and amyotrophic lateral sclerosis.",
        "category": "RNA-binding",
        "is_biomarker": True
    },
    {
        "name": "Neurofilament light chain",
        "description": "A biomarker for neuronal damage in various neurodegenerative diseases.",
        "category": "Cytoskeletal",
        "is_biomarker": True
    },
    {
        "name": "NfL",
        "description": "Abbreviation for Neurofilament light chain, a biomarker for neuronal damage.",
        "category": "Cytoskeletal",
        "is_biomarker": True
    },
    {
        "name": "Ubiquitin",
        "description": "A small protein involved in protein degradation, often found in protein aggregates in neurodegenerative diseases.",
        "category": "Protein degradation",
        "is_biomarker": False
    },
    {
        "name": "Prion protein",
        "description": "A protein that can misfold and cause prion diseases like Creutzfeldt-Jakob disease.",
        "category": "Prion",
        "is_biomarker": True
    },
    {
        "name": "PrP",
        "description": "Abbreviation for Prion protein, involved in prion diseases.",
        "category": "Prion",
        "is_biomarker": True
    },
    {
        "name": "Huntingtin",
        "description": "A protein that, when mutated, causes Huntington's disease.",
        "category": "Polyglutamine",
        "is_biomarker": False
    },
    {
        "name": "SOD1",
        "description": "Superoxide dismutase 1, a protein that, when mutated, can cause amyotrophic lateral sclerosis.",
        "category": "Antioxidant",
        "is_biomarker": False
    },
    {
        "name": "APOE",
        "description": "Apolipoprotein E, a protein involved in lipid metabolism. The APOE ε4 allele is a risk factor for Alzheimer's disease.",
        "category": "Lipoprotein",
        "is_biomarker": True
    },
    {
        "name": "APOE4",
        "description": "A variant of Apolipoprotein E that increases risk for Alzheimer's disease.",
        "category": "Lipoprotein",
        "is_biomarker": True
    }
]

# Insert each protein into the database
for protein in proteins:
    cursor.execute("""
        INSERT INTO proteins (name, description, category, is_biomarker)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Avoid duplicates if using a unique constraint
    """, (protein["name"], protein["description"], protein["category"], protein["is_biomarker"]))

conn.commit()
print("Proteins successfully inserted into the database.")

# Close the cursor and connection
cursor.close()
conn.close()