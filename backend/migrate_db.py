"""One-time migration to add design_documents table."""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_database.db")
print(f"Database: {db_path}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if design_documents table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='design_documents'")
exists = c.fetchone()

if not exists:
    c.execute("""
        CREATE TABLE design_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirement_id INTEGER REFERENCES requirements(id),
            file_names TEXT,
            file_paths TEXT,
            design_urls TEXT,
            analysis_result TEXT,
            folder_path VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("CREATE INDEX ix_design_documents_id ON design_documents (id)")
    print("Created: design_documents table")
else:
    print("Table design_documents already exists")

conn.commit()
conn.close()
print("Migration complete!")
