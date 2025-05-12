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

# Create the table for acronyms if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS acronyms (
        acronym_id SERIAL PRIMARY KEY,
        acronym VARCHAR NOT NULL,
        full_form VARCHAR NOT NULL,
        category VARCHAR,
        description TEXT
    );
""")
conn.commit()

# Define a list of common acronyms used in neurodegenerative disease research
acronyms = [
    {
        "acronym": "AD",
        "full_form": "Alzheimer's disease",
        "category": "Disease",
        "description": "A progressive neurodegenerative disease characterized by memory loss and cognitive decline."
    },
    {
        "acronym": "PD",
        "full_form": "Parkinson's disease",
        "category": "Disease",
        "description": "A neurodegenerative disorder affecting movement, often with tremors."
    },
    {
        "acronym": "HD",
        "full_form": "Huntington's disease",
        "category": "Disease",
        "description": "A hereditary disease causing progressive degeneration of nerve cells in the brain."
    },
    {
        "acronym": "ALS",
        "full_form": "Amyotrophic Lateral Sclerosis",
        "category": "Disease",
        "description": "A progressive neurodegenerative disease affecting nerve cells in the brain and spinal cord."
    },
    {
        "acronym": "FTD",
        "full_form": "Frontotemporal Dementia",
        "category": "Disease",
        "description": "A group of disorders caused by progressive nerve cell loss in the brain's frontal or temporal lobes."
    },
    {
        "acronym": "LBD",
        "full_form": "Lewy Body Dementia",
        "category": "Disease",
        "description": "A type of dementia characterized by abnormal deposits of a protein called alpha-synuclein."
    },
    {
        "acronym": "MCI",
        "full_form": "Mild Cognitive Impairment",
        "category": "Condition",
        "description": "A condition characterized by a slight but noticeable decline in cognitive abilities."
    },
    {
        "acronym": "CSF",
        "full_form": "Cerebrospinal Fluid",
        "category": "Biological",
        "description": "Clear, colorless fluid that surrounds the brain and spinal cord."
    },
    {
        "acronym": "BBB",
        "full_form": "Blood-Brain Barrier",
        "category": "Biological",
        "description": "A semipermeable border that separates the blood from the extracellular fluid in the central nervous system."
    },
    {
        "acronym": "MRI",
        "full_form": "Magnetic Resonance Imaging",
        "category": "Diagnostic",
        "description": "A medical imaging technique used to form pictures of the anatomy and physiological processes of the body."
    },
    {
        "acronym": "PET",
        "full_form": "Positron Emission Tomography",
        "category": "Diagnostic",
        "description": "A functional imaging technique that uses radioactive substances to visualize and measure metabolic processes in the body."
    },
    {
        "acronym": "EEG",
        "full_form": "Electroencephalography",
        "category": "Diagnostic",
        "description": "A monitoring method to record electrical activity of the brain."
    },
    {
        "acronym": "MMSE",
        "full_form": "Mini-Mental State Examination",
        "category": "Assessment",
        "description": "A 30-point questionnaire used to measure cognitive impairment."
    },
    {
        "acronym": "APOE",
        "full_form": "Apolipoprotein E",
        "category": "Genetic",
        "description": "A protein involved in metabolism of fats in the body, with certain variants linked to Alzheimer's disease risk."
    },
    {
        "acronym": "NFT",
        "full_form": "Neurofibrillary Tangles",
        "category": "Pathology",
        "description": "Abnormal accumulations of a protein called tau inside neurons, characteristic of Alzheimer's disease."
    },
    {
        "acronym": "Aβ",
        "full_form": "Amyloid Beta",
        "category": "Protein",
        "description": "A peptide of amino acids that is the main component of amyloid plaques found in Alzheimer's disease."
    },
    {
        "acronym": "NfL",
        "full_form": "Neurofilament Light Chain",
        "category": "Biomarker",
        "description": "A biomarker for neuronal damage in various neurodegenerative diseases."
    },
    {
        "acronym": "WM",
        "full_form": "Working Memory",
        "category": "Cognitive",
        "description": "A cognitive system for temporarily holding and manipulating information."
    },
    {
        "acronym": "EM",
        "full_form": "Episodic Memory",
        "category": "Cognitive",
        "description": "The memory of autobiographical events and their associated emotions and contexts."
    },
    {
        "acronym": "CNS",
        "full_form": "Central Nervous System",
        "category": "Anatomical",
        "description": "The part of the nervous system consisting of the brain and spinal cord."
    }
]

# Insert each acronym into the database
for acronym_entry in acronyms:
    cursor.execute("""
        INSERT INTO acronyms (acronym, full_form, category, description)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Avoid duplicates if using a unique constraint
    """, (acronym_entry["acronym"], acronym_entry["full_form"], acronym_entry["category"], acronym_entry["description"]))

conn.commit()
print("Acronyms successfully inserted into the database.")

# Close the cursor and connection
cursor.close()
conn.close()