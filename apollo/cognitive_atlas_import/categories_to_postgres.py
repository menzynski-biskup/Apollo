from datetime import datetime

import requests
import psycopg2

# Define the URL for the Cognitive Atlas concept endpoint
url = "http://cognitiveatlas.org/api/v-alpha/concept"

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cognitive_concepts (
        concept_id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        concept_class VARCHAR,
        definition_text TEXT,
        creation_time BIGINT,
        event_stamp TIMESTAMP
    );
""")
conn.commit()

# Send GET request to fetch data from the Cognitive Atlas API
response = requests.get(url)

# Check if the response status is OK (HTTP 200)
if response.status_code == 200:
    data = response.json()  # Parse the JSON response

    # Insert each concept into the database
    for concept in data:
        concept_id = concept.get('id', 'No ID found')
        concept_name = concept.get('name', 'No Name found')
        concept_class = concept.get('id_concept_class', 'No Class')
        definition_text = concept.get('definition_text', 'No Definition')
        creation_time = concept.get('creation_time', 0)
        event_stamp = concept.get('event_stamp', 'No Event Stamp')

        # Handle missing or invalid event_stamp
        if event_stamp == "No Event Stamp" or event_stamp is None:
            event_stamp = None  # NULL for missing or invalid event_stamp
        else:
            try:
                event_stamp = int(event_stamp)  # Try to convert event_stamp to an integer (timestamp)
                event_stamp = datetime.fromtimestamp(event_stamp / 1000)  # Convert from milliseconds to seconds
            except ValueError:
                event_stamp = None  # If conversion fails, set to NULL

        # Insert data into the cognitive_concepts table
        cursor.execute("""
            INSERT INTO cognitive_concepts (concept_id, name, concept_class, definition_text, creation_time, event_stamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (concept_id) DO NOTHING;  -- Avoid duplicates
        """, (concept_id, concept_name, concept_class, definition_text, creation_time, event_stamp))

    conn.commit()
    print("Concepts successfully inserted into the database.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

# Close the cursor and connection
cursor.close()
conn.close()