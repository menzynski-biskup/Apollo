import requests
import psycopg2
import json

# PostgreSQL connection
conn = psycopg2.connect("dbname=postgres user=postgres password=")
cur = conn.cursor()

# Fetch concept_ids from your PostgreSQL database
cur.execute("SELECT concept_id FROM cognitive_concepts;")
concept_ids = cur.fetchall()


# Function to fetch JSON from the Cognitive Atlas API
def fetch_concept_data(concept_id):
    url = f"https://www.cognitiveatlas.org/concept/json/{concept_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {concept_id}")
        return None


# Function to update or create concept classes
def update_concept_classes(concept_classes):
    for concept_class in concept_classes:
        cur.execute("""
            INSERT INTO concept_classes (concept_class_id, name, description, display_order)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (concept_class_id) DO UPDATE
            SET name = EXCLUDED.name, description = EXCLUDED.description, display_order = EXCLUDED.display_order;
        """, (concept_class['id'], concept_class['name'], concept_class['description'], concept_class['display_order']))
    conn.commit()


# Function to update or create relationships
def update_relationships(relationships):
    for relationship in relationships:
        cur.execute("""
            INSERT INTO relationships (concept_id, related_concept_id, relationship, direction)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (concept_id, related_concept_id) DO UPDATE
            SET relationship = EXCLUDED.relationship, direction = EXCLUDED.direction;
        """, (relationship['concept_id'], relationship['related_concept_id'], relationship['relationship'],
              relationship['direction']))
    conn.commit()


# Iterate through concept_ids and fetch relevant data
for concept_id_tuple in concept_ids:
    concept_id = concept_id_tuple[0]
    data = fetch_concept_data(concept_id)

    if data:
        # Extract relevant information for concept classes, relationships, contrasts, etc.
        if 'conceptclasses' in data:
            update_concept_classes(data['conceptclasses'])

        if 'relationships' in data:
            for relationship in data['relationships']:
                # Assuming you have a `concept_id` in the relationship data as well
                related_concept_id = relationship.get('id', '')
                relationship_type = relationship.get('relationship', '')
                direction = relationship.get('direction', '')

                # Insert relationship into the database
                update_relationships([{
                    'concept_id': concept_id,
                    'related_concept_id': related_concept_id,
                    'relationship': relationship_type,
                    'direction': direction
                }])

        if 'contrasts' in data:
            # Handle contrasts as well (similar approach)
            for contrast in data['contrasts']:
                task_id = contrast.get('task_id', '')
                relationship_type = contrast.get('relationship', '')
                update_relationships([{
                    'concept_id': concept_id,
                    'related_concept_id': task_id,
                    'relationship': relationship_type,
                    'direction': 'MEASUREDBY'
                }])

# Close the PostgreSQL connection
cur.close()
conn.close()