"""
Database Migration v2 — Additive Schema Upgrade
-------------------------------------------------
Adds the following columns to 'test_cases' table:
  • created_at       DATETIME  (default CURRENT_TIMESTAMP)
  • complexity_score  INTEGER   (default 1)
  • duplicate_score   REAL      (default 0.0)
  • coverage_tag      VARCHAR   (default '')

Safe: Uses ALTER TABLE ADD COLUMN — no data loss.
Run BEFORE updating models.py.
"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_database.db")
print(f"Database: {db_path}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Helper: check if a column already exists
def column_exists(table: str, column: str) -> bool:
    c.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in c.fetchall()]
    return column in columns

migrations = [
    ("test_cases", "created_at",       "ALTER TABLE test_cases ADD COLUMN created_at DATETIME"),
    ("test_cases", "complexity_score",  "ALTER TABLE test_cases ADD COLUMN complexity_score INTEGER DEFAULT 1"),
    ("test_cases", "duplicate_score",   "ALTER TABLE test_cases ADD COLUMN duplicate_score REAL DEFAULT 0.0"),
    ("test_cases", "coverage_tag",      "ALTER TABLE test_cases ADD COLUMN coverage_tag VARCHAR(100) DEFAULT ''"),
]

applied = 0
for table, col, sql in migrations:
    if column_exists(table, col):
        print(f"  ✓ {table}.{col} already exists — skipping")
    else:
        c.execute(sql)
        print(f"  + Added {table}.{col}")
        applied += 1

conn.commit()
conn.close()
print(f"\nMigration complete! Applied {applied} change(s).")
