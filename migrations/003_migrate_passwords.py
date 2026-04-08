"""
Migración 003: Migrar contraseñas SHA-256 legacy a bcrypt.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.config import SessionLocal
from src.models.entities import User

def migrate():
    db = SessionLocal()
    try:
        bcrypt_count = 0
        legacy_count = 0
        
        users = db.query(User).all()
        for user in users:
            if user.password_hash and len(user.password_hash) == 64:
                print(f"Legacy (requiere re-establecer contraseña): {user.username}")
                legacy_count += 1
            elif user.password_hash and len(user.password_hash) == 60 and user.password_hash.startswith('$2'):
                print(f"Ya es bcrypt: {user.username}")
                bcrypt_count += 1
        
        print(f"\nResumen: {bcrypt_count} usuarios en bcrypt, {legacy_count} legacy (sin login reciente)")
    
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
