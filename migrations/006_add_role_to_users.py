"""Migration 006: Add role field to users."""
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
    
    # Agregar role a users
    print("\n--- Adding 'role' to 'users' table ---")
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'role' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'vendedor'")
        # Actualizar admin existente
        cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
        print("✓ Column 'role' added and admin updated")
    else:
        print("- Column 'role' already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Migration 006 completed!")

if __name__ == "__main__":
    migrate()