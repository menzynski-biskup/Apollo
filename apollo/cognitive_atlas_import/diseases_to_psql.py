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

# Create the table for diseases if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS diseases (
        disorder_id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        definition TEXT,
        event_stamp TIMESTAMP,
        id_protocol VARCHAR,
        flag_for_curator INTEGER,
        creation_time BIGINT,
        last_updated BIGINT
    );
""")
conn.commit()

# URL to fetch tasks from the Cognitive Atlas API
url = "https://www.cognitiveatlas.org/api/v-alpha/disorder"

# Send GET request to fetch data from the Cognitive Atlas API
response = requests.get(url)

# Check if the response status is OK (HTTP 200)
if response.status_code == 200:
    disorders = response.json()  # Parse the JSON response


    # Insert each disease into the database
    for disorder in disorders:
        disorder_id = disorder.get('id', 'No ID found')
        disorder_name = disorder.get('name', 'No Name found')
        definition = disorder.get('definition', 'No Definition')
        event_stamp = disorder.get('event_stamp', 'No Event Stamp')
        id_protocol = disorder.get('id_protocol', 'No Protocol')
        flag_for_curator = disorder.get('flag_for_curator', 0)
        creation_time = disorder.get('creation_time', 0)
        last_updated = disorder.get('last_updated', 0)

        # Convert event_stamp to timestamp if it is a valid string (ISO format)
        if event_stamp != 'No Event Stamp':
            try:
                event_stamp = datetime.fromisoformat(event_stamp)
            except ValueError:
                event_stamp = None  # If invalid format, set to None (NULL in DB)
        else:
            event_stamp = None



        # Insert data into the diseases table
        cursor.execute("""
            INSERT INTO diseases (disorder_id, name, definition, event_stamp, id_protocol, flag_for_curator, creation_time, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (disorder_id) DO NOTHING;  -- Avoid duplicates
        """, (disorder_id, disorder_name, definition, event_stamp, id_protocol, flag_for_curator, creation_time, last_updated))

    conn.commit()
    print("Diseases successfully inserted into the database.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

# Close the cursor and connection
cursor.close()
conn.close()