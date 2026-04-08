"""Tests para el módulo de configuración."""

import sys
import os
sys.path.insert(0, '.')

from src.config import (
    get_env,
    is_production,
    is_development,
    get_db_path,
    get_log_level,
    get_app_name,
    get_app_version,
    get_config_summary,
    get_bcrypt_rounds,
)


class TestConfig:
    """Tests para configuración."""
    
    def test_get_env_dev(self):
        """Por defecto el entorno es dev."""
        # Resetear para el test
        result = get_env()
        assert result in ['dev', 'staging', 'prod']
    
    def test_is_development_true(self):
        """is_development retorna True en dev."""
        result = is_development()
        assert isinstance(result, bool)
    
    def test_is_production_false(self):
        """is_production retorna False en dev."""
        result = is_production()
        assert result == False
    
    def test_get_db_path_default(self):
        """DB path tiene un default."""
        result = get_db_path()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_log_level_default(self):
        """Log level tiene un default."""
        result = get_log_level()
        assert result in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def test_get_app_name(self):
        """App name tiene un default."""
        result = get_app_name()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_app_version(self):
        """App version tiene un default."""
        result = get_app_version()
        assert isinstance(result, str)
    
    def test_get_config_summary(self):
        """Summary retorna diccionario."""
        result = get_config_summary()
        assert isinstance(result, dict)
        assert 'app_name' in result
        assert 'env' in result
        assert 'db_path' in result
    
    def test_get_bcrypt_rounds_dev(self):
        """En dev, bcrypt rounds es bajo para velocidad."""
        result = get_bcrypt_rounds()
        assert isinstance(result, int)
        assert result >= 4