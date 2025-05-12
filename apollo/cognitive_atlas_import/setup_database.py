import os
import subprocess
import sys

def run_script(script_name):
    """Run a Python script and print its output."""
    print(f"Running {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run all database setup scripts."""
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of scripts to run
    scripts = [
        "diseases_to_psql.py",
        "symptoms_to_psql.py",
        "proteins_to_psql.py",
        "brain_regions_to_psql.py",
        "acronyms_to_psql.py",
        "tasks_to_psql.py",  # If this exists
        "categories_to_postgres.py",  # If this exists
        "relationships.py"  # If this exists
    ]
    
    # Run each script
    success_count = 0
    for script in scripts:
        script_path = os.path.join(current_dir, script)
        if os.path.exists(script_path):
            if run_script(script_path):
                success_count += 1
        else:
            print(f"Script {script} not found, skipping.")
    
    print(f"\nDatabase setup complete. Successfully ran {success_count} out of {len(scripts)} scripts.")
    print("The database is now populated with predefined entity lists for improved entity recognition.")

if __name__ == "__main__":
    main()