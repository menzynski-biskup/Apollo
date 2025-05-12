import json
import pprint

# Load the JSON file
with open('data/brain_regions/json/NeuroNames.json', 'r') as f:
    data = json.load(f)

# Print the number of entries
print(f"Total number of entries: {len(data)}")

# Print the keys of the first entry to understand the structure
print("\nKeys in the first entry:")
print(list(data[0].keys()))

# Print a sample entry with pretty formatting
print("\nSample entry (first entry):")
pprint.pprint(data[0], depth=2)

# Check if there are entries with parents
has_parents = [entry for entry in data[:10] if 'parents' in entry and entry['parents']]
if has_parents:
    print("\nSample entry with parents:")
    pprint.pprint(has_parents[0], depth=3)

# Check if there are entries with synonyms
has_synonyms = [entry for entry in data[:10] if 'synonyms' in entry and entry['synonyms']]
if has_synonyms:
    print("\nSample entry with synonyms:")
    pprint.pprint(has_synonyms[0], depth=3)