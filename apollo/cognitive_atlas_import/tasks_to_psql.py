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

# Create the table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        definition_text TEXT,
        alias VARCHAR,
        creation_time BIGINT,
        event_stamp TIMESTAMP,
        review_status VARCHAR,
        def_id VARCHAR,
        def_id_user VARCHAR,
        def_event_stamp TIMESTAMP
    );
""")
conn.commit()

# URL to fetch tasks from the Cognitive Atlas API
url = "https://www.cognitiveatlas.org/api/v-alpha/task"

# Send GET request to fetch data from the Cognitive Atlas API
response = requests.get(url)

# Check if the response status is OK (HTTP 200)
if response.status_code == 200:
    data = response.json()  # Parse the JSON response

    # Insert each task into the database
    for task in data:
        task_id = task.get('id', 'No ID found')
        task_name = task.get('name', 'No Name found')
        definition_text = task.get('definition_text', 'No Definition')
        alias = task.get('alias', 'No Alias')
        creation_time = task.get('creation_time', 0)
        event_stamp = task.get('event_stamp', 'No Event Stamp')
        review_status = task.get('review_status', 'No Review Status')
        def_id = task.get('def_id', 'No Def ID')
        def_id_user = task.get('def_id_user', 'No Def ID User')
        def_event_stamp = task.get('def_event_stamp', 'No Def Event Stamp')

        # Convert event_stamp to timestamp if it is a valid string (ISO format)
        if event_stamp != 'No Event Stamp' and event_stamp != 'No Def Event Stamp':
            try:
                event_stamp = datetime.fromisoformat(event_stamp)
            except ValueError:
                event_stamp = None  # If invalid format, set to None (NULL in DB)
        else:
            event_stamp = None  # If it's 'No Event Stamp', set to None (NULL in DB)

        # Convert def_event_stamp to timestamp if it is a valid string (ISO format)
        if def_event_stamp != 'No Def Event Stamp':
            try:
                def_event_stamp = datetime.fromisoformat(def_event_stamp)
            except ValueError:
                def_event_stamp = None  # If invalid format, set to None (NULL in DB)
        else:
            def_event_stamp = None  # If it's 'No Def Event Stamp', set to None (NULL in DB)

        # Insert data into the tasks table
        cursor.execute("""
            INSERT INTO tasks (task_id, name, definition_text, alias, creation_time, event_stamp, review_status, def_id, def_id_user, def_event_stamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (task_id) DO NOTHING;  -- Avoid duplicates
        """, (task_id, task_name, definition_text, alias, creation_time, event_stamp, review_status, def_id, def_id_user, def_event_stamp))

    conn.commit()
    print("Tasks successfully inserted into the database.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

# Close the cursor and connection
cursor.close()
conn.close()