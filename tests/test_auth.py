"""Tests para el módulo de autenticación."""

import sys
sys.path.insert(0, '.')

from src.utils.auth import hash_password, verify_password, migrate_to_bcrypt


class TestHashPassword:
    """Tests para hash_password."""
    
    def test_hash_genera_string(self):
        """El hash debe generar un string."""
        result = hash_password("password123")
        assert isinstance(result, str)
    
    def test_hash_tiene_longitud_correcta(self):
        """El hash bcrypt tiene ~60 caracteres."""
        result = hash_password("password123")
        assert len(result) == 60
    
    def test_hash_empieza_con_2a(self):
        """Los hashes bcrypt empiezan con $2a$ o $2b$."""
        result = hash_password("password123")
        assert result.startswith('$2')
    
    def test_diferentes_hashes_para_misma_password(self):
        """Cada hash debe ser diferente (salt aleatorio)."""
        hash1 = hash_password("password123")
        hash2 = hash_password("password123")
        assert hash1 != hash2


class TestVerifyPassword:
    """Tests para verify_password."""
    
    def test_password_correcta(self):
        """Verifica password correcta."""
        hashed = hash_password("password123")
        result, _ = verify_password("password123", hashed)
        assert result == True
    
    def test_password_incorrecta(self):
        """Password incorrecta retorna False."""
        hashed = hash_password("password123")
        result, _ = verify_password("wrongpassword", hashed)
        assert result == False
    
    def test_hash_legacy_sha256(self):
        """Verifica hash legacy SHA256."""
        import hashlib
        legacy_hash = hashlib.sha256("password123".encode()).hexdigest()
        result, is_legacy = verify_password("password123", legacy_hash)
        assert result == True
        assert is_legacy == True
    
    def test_hash_invalido(self):
        """Hash inválido retorna False."""
        result, _ = verify_password("password123", "invalid_hash")
        assert result == False


class TestMigrateToBcrypt:
    """Tests para migrate_to_bcrypt."""
    
    def test_migration_genera_bcrypt(self):
        """La migración genera hash bcrypt."""
        result = migrate_to_bcrypt("password123", "old_hash")
        assert result.startswith('$2')
    
    def test_migration_acepta_cualquier_old_hash(self):
        """La migración funciona con cualquier old hash."""
        result = migrate_to_bcrypt("password123", "sha256_legacy_hash")
        assert result.startswith('$2')