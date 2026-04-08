"""
Módulo de autenticación segura con bcrypt.
Usa variables de entorno de src/config.py
"""
import bcrypt
from typing import Tuple
from src.config import get_bcrypt_rounds

# Rounds desde config (12 en prod, 4 en dev)
BCRYPT_ROUNDS = get_bcrypt_rounds()

def hash_password(password: str) -> str:
    """Genera hash bcrypt de una contraseña."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> Tuple[bool, bool]:
    """Verifica una contraseña contra un hash."""
    if len(password_hash) == 60 and password_hash.startswith('$2'):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')), False
    
    elif len(password_hash) == 64:
        import hashlib
        computed = hashlib.sha256(password.encode()).hexdigest()
        return computed == password_hash, True
    
    return False, False


def migrate_to_bcrypt(password: str, old_hash: str) -> str:
    """Migra una contraseña legacy a bcrypt."""
    return hash_password(password)
