"""Migration 004: Add categories table."""
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
    
    print("\n--- Creating 'categories' table ---")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(255),
            parent_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        )
    """)
    print("✓ Table 'categories' created")
    
    print("\n--- Adding 'category_id' to 'products' table ---")
    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'category_id' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id)")
        print("✓ Column 'category_id' added to 'products'")
    else:
        print("- Column 'category_id' already exists")
    
    print("\n--- Creating default category ---")
    cursor.execute("""
        INSERT OR IGNORE INTO categories (name, description, parent_id, is_active, created_at)
        VALUES ('Sin Categoría', 'Categoría por defecto para productos sin clasificar', NULL, 1, datetime('now'))
    """)
    print("✓ Default category created")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Migration 004 completed successfully!")


if __name__ == "__main__":
    migrate()