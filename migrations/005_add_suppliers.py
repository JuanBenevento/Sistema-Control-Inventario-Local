"""Migration 005: Add suppliers table."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.config import DATABASE_URL


def get_db_path():
    return DATABASE_URL.replace("sqlite:///", "")


def migrate():
    db_path = get_db_path()
    print(f"Database: {db_path}")
    
    if not Path(db_path).exists():
        print("ERROR: Database does not exist.")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n--- Creating 'suppliers' table ---")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(150) NOT NULL,
            contact_name VARCHAR(100),
            phone VARCHAR(30),
            email VARCHAR(100),
            address VARCHAR(255),
            notes VARCHAR(500),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    print("✓ Table 'suppliers' created")
    
    print("\n--- Adding 'supplier_id' to 'products' table ---")
    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'supplier_id' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN supplier_id INTEGER REFERENCES suppliers(id)")
        print("✓ Column 'supplier_id' added to 'products'")
    else:
        print("- Column 'supplier_id' already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Migration 005 completed successfully!")


if __name__ == "__main__":
    migrate()