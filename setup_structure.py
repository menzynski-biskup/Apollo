import os

project_structure = [
    "apollo/__init__.py",
    "apollo/ner/__init__.py",
    "apollo/ner/extractor.py",
    "apollo/ner/postprocess.py",
    "apollo/data_ingest/__init__.py",
    "apollo/data_ingest/pdf_parser.py",
    "apollo/data_ingest/cleaner.py",
    "apollo/schemas/__init__.py",
    "apollo/schemas/entities.py",
    "apollo/storage/__init__.py",
    "apollo/storage/json_exporter.py",
    "apollo/storage/db_interface.py",
    "apollo/utils/__init__.py",
    "apollo/utils/logger.py",
    "notebooks/ner_demo.ipynb",
    "tests/test_ner.py",
    "tests/test_pdf_parser.py",
    "data/sample_paper.pdf",
    "scripts/extract_entities.py",
    "/requirements.txt",
    "/pyproject.toml",
    "/README.md",
    ".gitignore"
]

for path in project_structure:
    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    if not path.endswith("/"):
        with open(path, "w") as f:
            f.write("# " + os.path.basename(path) + "\n")

print("✅ Apollo project structure created.")