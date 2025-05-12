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

# Create the table for symptoms if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS symptoms (
        symptom_id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        definition TEXT,
        related_diseases TEXT,
        category VARCHAR
    );
""")
conn.commit()

# Define a list of common symptoms in neurodegenerative diseases
symptoms = [
    {
        "name": "Memory loss",
        "definition": "Difficulty in recalling information or events, particularly recent ones.",
        "related_diseases": "Alzheimer's disease, Mild Cognitive Impairment, Vascular Dementia",
        "category": "Cognitive"
    },
    {
        "name": "Cognitive decline",
        "definition": "Progressive deterioration of cognitive functions including memory, attention, and problem-solving.",
        "related_diseases": "Alzheimer's disease, Frontotemporal Dementia, Lewy Body Dementia",
        "category": "Cognitive"
    },
    {
        "name": "Executive dysfunction",
        "definition": "Impairment in cognitive processes that regulate, control, and manage other cognitive processes.",
        "related_diseases": "Frontotemporal Dementia, Parkinson's disease, Huntington's disease",
        "category": "Cognitive"
    },
    {
        "name": "Aphasia",
        "definition": "Language disorder that affects a person's ability to communicate.",
        "related_diseases": "Primary Progressive Aphasia, Frontotemporal Dementia, Alzheimer's disease",
        "category": "Language"
    },
    {
        "name": "Anomia",
        "definition": "Difficulty in finding words or naming objects.",
        "related_diseases": "Alzheimer's disease, Semantic Dementia, Primary Progressive Aphasia",
        "category": "Language"
    },
    {
        "name": "Apraxia",
        "definition": "Inability to perform purposeful movements despite having the physical ability to do so.",
        "related_diseases": "Alzheimer's disease, Corticobasal Degeneration, Progressive Supranuclear Palsy",
        "category": "Motor"
    },
    {
        "name": "Tremor",
        "definition": "Involuntary, rhythmic muscle contraction leading to shaking movements.",
        "related_diseases": "Parkinson's disease, Essential Tremor, Multiple System Atrophy",
        "category": "Motor"
    },
    {
        "name": "Bradykinesia",
        "definition": "Slowness of movement.",
        "related_diseases": "Parkinson's disease, Progressive Supranuclear Palsy, Multiple System Atrophy",
        "category": "Motor"
    },
    {
        "name": "Rigidity",
        "definition": "Stiffness or inflexibility of the limbs or joints.",
        "related_diseases": "Parkinson's disease, Progressive Supranuclear Palsy, Corticobasal Degeneration",
        "category": "Motor"
    },
    {
        "name": "Postural instability",
        "definition": "Impaired balance and coordination leading to falls.",
        "related_diseases": "Parkinson's disease, Progressive Supranuclear Palsy, Multiple System Atrophy",
        "category": "Motor"
    },
    {
        "name": "Chorea",
        "definition": "Involuntary, irregular, and flowing movements.",
        "related_diseases": "Huntington's disease, Neuroacanthocytosis, Sydenham's chorea",
        "category": "Motor"
    },
    {
        "name": "Dystonia",
        "definition": "Sustained or intermittent muscle contractions causing abnormal postures.",
        "related_diseases": "Parkinson's disease, Dystonia Musculorum Deformans, Wilson's disease",
        "category": "Motor"
    },
    {
        "name": "Ataxia",
        "definition": "Lack of muscle coordination during voluntary movements.",
        "related_diseases": "Spinocerebellar Ataxia, Multiple System Atrophy, Friedreich's Ataxia",
        "category": "Motor"
    },
    {
        "name": "Dysphagia",
        "definition": "Difficulty in swallowing.",
        "related_diseases": "Amyotrophic Lateral Sclerosis, Parkinson's disease, Progressive Bulbar Palsy",
        "category": "Bulbar"
    },
    {
        "name": "Dysarthria",
        "definition": "Difficulty in articulating speech.",
        "related_diseases": "Amyotrophic Lateral Sclerosis, Parkinson's disease, Multiple Sclerosis",
        "category": "Bulbar"
    },
    {
        "name": "Visual hallucinations",
        "definition": "Seeing things that are not present.",
        "related_diseases": "Lewy Body Dementia, Parkinson's disease with dementia, Charles Bonnet Syndrome",
        "category": "Psychiatric"
    },
    {
        "name": "Depression",
        "definition": "Persistent feelings of sadness and loss of interest.",
        "related_diseases": "Parkinson's disease, Alzheimer's disease, Huntington's disease",
        "category": "Psychiatric"
    },
    {
        "name": "Anxiety",
        "definition": "Feelings of worry, nervousness, or unease.",
        "related_diseases": "Parkinson's disease, Alzheimer's disease, Multiple Sclerosis",
        "category": "Psychiatric"
    },
    {
        "name": "Apathy",
        "definition": "Lack of interest, enthusiasm, or concern.",
        "related_diseases": "Frontotemporal Dementia, Alzheimer's disease, Parkinson's disease",
        "category": "Psychiatric"
    },
    {
        "name": "Disinhibition",
        "definition": "Lack of restraint manifested as disregard for social conventions.",
        "related_diseases": "Frontotemporal Dementia, Huntington's disease, Alcohol-Related Dementia",
        "category": "Psychiatric"
    },
    {
        "name": "Sleep disturbances",
        "definition": "Abnormal sleep patterns including insomnia, hypersomnia, or parasomnia.",
        "related_diseases": "Parkinson's disease, Lewy Body Dementia, Alzheimer's disease",
        "category": "Sleep"
    },
    {
        "name": "REM sleep behavior disorder",
        "definition": "A sleep disorder characterized by acting out vivid dreams during REM sleep.",
        "related_diseases": "Parkinson's disease, Lewy Body Dementia, Multiple System Atrophy",
        "category": "Sleep"
    },
    {
        "name": "Olfactory dysfunction",
        "definition": "Impaired sense of smell.",
        "related_diseases": "Parkinson's disease, Alzheimer's disease, Lewy Body Dementia",
        "category": "Sensory"
    },
    {
        "name": "Visuospatial deficits",
        "definition": "Difficulty in perceiving and interacting with objects in space.",
        "related_diseases": "Alzheimer's disease, Posterior Cortical Atrophy, Lewy Body Dementia",
        "category": "Cognitive"
    }
]

# Insert each symptom into the database
for symptom in symptoms:
    cursor.execute("""
        INSERT INTO symptoms (name, definition, related_diseases, category)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Avoid duplicates if using a unique constraint
    """, (symptom["name"], symptom["definition"], symptom["related_diseases"], symptom["category"]))

conn.commit()
print("Symptoms successfully inserted into the database.")

# Close the cursor and connection
cursor.close()
conn.close()