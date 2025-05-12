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

# Create the table for brain regions if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS brain_regions (
        region_id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        parent_region VARCHAR,
        related_functions TEXT
    );
""")
conn.commit()

# Define a list of common brain regions relevant to neurodegenerative diseases
brain_regions = [
    {
        "name": "Hippocampus",
        "description": "A brain structure embedded deep in the temporal lobe, important for learning and memory.",
        "parent_region": "Limbic system",
        "related_functions": "Memory formation, spatial navigation"
    },
    {
        "name": "Amygdala",
        "description": "An almond-shaped structure in the temporal lobe, involved in emotional processing.",
        "parent_region": "Limbic system",
        "related_functions": "Emotional responses, fear conditioning"
    },
    {
        "name": "Frontal lobe",
        "description": "The largest lobe of the brain, responsible for executive functions.",
        "parent_region": "Cerebral cortex",
        "related_functions": "Executive function, decision making, personality"
    },
    {
        "name": "Prefrontal cortex",
        "description": "The anterior part of the frontal lobe, involved in complex cognitive behavior.",
        "parent_region": "Frontal lobe",
        "related_functions": "Executive function, working memory, planning"
    },
    {
        "name": "Temporal lobe",
        "description": "One of the four major lobes of the cerebral cortex, involved in auditory processing and memory.",
        "parent_region": "Cerebral cortex",
        "related_functions": "Auditory processing, memory, language"
    },
    {
        "name": "Parietal lobe",
        "description": "One of the four major lobes of the cerebral cortex, involved in sensory processing.",
        "parent_region": "Cerebral cortex",
        "related_functions": "Sensory processing, spatial awareness"
    },
    {
        "name": "Occipital lobe",
        "description": "One of the four major lobes of the cerebral cortex, involved in visual processing.",
        "parent_region": "Cerebral cortex",
        "related_functions": "Visual processing"
    },
    {
        "name": "Entorhinal cortex",
        "description": "An area of the brain located in the medial temporal lobe, important for memory and navigation.",
        "parent_region": "Temporal lobe",
        "related_functions": "Memory, spatial navigation"
    },
    {
        "name": "Basal ganglia",
        "description": "A group of subcortical nuclei involved in motor control and learning.",
        "parent_region": "Subcortical",
        "related_functions": "Motor control, procedural learning"
    },
    {
        "name": "Substantia nigra",
        "description": "A brain structure located in the midbrain, important for movement and reward.",
        "parent_region": "Midbrain",
        "related_functions": "Motor control, dopamine production"
    },
    {
        "name": "Thalamus",
        "description": "A structure located between the cerebral cortex and the midbrain, relaying sensory and motor signals.",
        "parent_region": "Diencephalon",
        "related_functions": "Sensory and motor signal relay"
    },
    {
        "name": "Hypothalamus",
        "description": "A region of the brain that controls many body functions including hunger, thirst, and temperature.",
        "parent_region": "Diencephalon",
        "related_functions": "Homeostasis, hormone regulation"
    },
    {
        "name": "Cerebellum",
        "description": "A structure at the back of the brain, important for motor control and some cognitive functions.",
        "parent_region": "Hindbrain",
        "related_functions": "Motor coordination, balance, some cognitive functions"
    },
    {
        "name": "Brainstem",
        "description": "The part of the brain that connects the cerebrum with the spinal cord, controlling basic functions.",
        "parent_region": "Hindbrain",
        "related_functions": "Basic life functions, arousal, sleep"
    },
    {
        "name": "Locus coeruleus",
        "description": "A nucleus in the brainstem involved in physiological responses to stress and panic.",
        "parent_region": "Brainstem",
        "related_functions": "Stress response, arousal"
    },
    {
        "name": "Nucleus basalis of Meynert",
        "description": "A group of neurons in the basal forebrain, important for attention and memory.",
        "parent_region": "Basal forebrain",
        "related_functions": "Attention, memory, acetylcholine production"
    },
    {
        "name": "Cingulate cortex",
        "description": "A part of the brain situated in the medial aspect of the cerebral cortex, involved in emotion and cognition.",
        "parent_region": "Limbic system",
        "related_functions": "Emotion, cognition, pain processing"
    },
    {
        "name": "Corpus callosum",
        "description": "A broad band of nerve fibers that connects the left and right hemispheres of the brain.",
        "parent_region": "Cerebral cortex",
        "related_functions": "Interhemispheric communication"
    }
]

# Insert each brain region into the database
for region in brain_regions:
    cursor.execute("""
        INSERT INTO brain_regions (name, description, parent_region, related_functions)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;  -- Avoid duplicates if using a unique constraint
    """, (region["name"], region["description"], region["parent_region"], region["related_functions"]))

conn.commit()
print("Brain regions successfully inserted into the database.")

# Close the cursor and connection
cursor.close()
conn.close()