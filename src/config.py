"""
Configuración centralizada del proyecto via variables de entorno.
 =================================================================
Permite configurar la aplicación sin hardcodear valores.
Carga automáticamente desde archivo .env si existe.
"""

import os
from pathlib import Path
from typing import Optional

# ==============================================================================
# RUTAS - Definidas primero para que estén disponibles al cargar .env
# ==============================================================================

def get_project_root() -> Path:
    """Retorna la raíz del proyecto."""
    # src/config.py -> src -> proyecto (2 niveles arriba)
    return Path(__file__).parent.parent

# ==============================================================================
# CARGAR .ENV SI EXISTE
# ==============================================================================

def _load_env_file():
    """Carga variables desde .env si existe."""
    root = get_project_root()
    env_file = root / '.env'
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

# Cargar .env al importar
_load_env_file()

# ==============================================================================
# RUTAS - Funciones de utilidad
# ==============================================================================

def get_project_root() -> Path:
    """Retorna la raíz del proyecto."""
    return Path(__file__).parent.parent

def get_db_path() -> str:
    """Ruta de la base de datos."""
    return os.environ.get('DB_PATH', 'data/inventory.db')

def get_log_file() -> str:
    """Ruta del archivo de log."""
    return os.environ.get('LOG_FILE', 'logs/app.log')

def get_data_dir() -> Path:
    """Directorio de datos."""
    root = get_project_root()
    db_path = get_db_path()
    # Si es ruta relativa, relative al root
    if not os.path.isabs(db_path):
        return root / 'data'
    return Path(db_path).parent

def get_logs_dir() -> Path:
    """Directorio de logs."""
    root = get_project_root()
    log_file = get_log_file()
    if not os.path.isabs(log_file):
        return root / 'logs'
    return Path(log_file).parent

# ==============================================================================
# DATABASE
# ==============================================================================

def get_database_url() -> str:
    """URL de conexión a la base de datos."""
    db_path = get_db_path()
    
    # Si es ruta absoluta
    if os.path.isabs(db_path):
        return f"sqlite:///{db_path}"
    
    # Ruta relativa - convertir a absoluta
    root = get_project_root()
    abs_path = root / db_path
    return f"sqlite:///{abs_path}"

def get_db_echo() -> bool:
    """Si True, muestra SQL en logs (solo para desarrollo)."""
    env = os.environ.get('ENV', 'dev').lower()
    return env == 'dev'

# ==============================================================================
# LOGGING
# ==============================================================================

def get_log_level() -> str:
    """Nivel de logging."""
    return os.environ.get('LOG_LEVEL', 'INFO').upper()

def get_log_format() -> str:
    """Formato de log."""
    env = os.environ.get('ENV', 'dev').lower()
    
    if env == 'prod':
        # Formato JSON para producción
        return '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Formato legible para desarrollo
    return '%(levelname)s | %(message)s'

def get_log_rotation() -> bool:
    """Si True, rota los logs (máx 10MB, 5 archivos)."""
    env = os.environ.get('ENV', 'dev').lower()
    return env == 'prod'

# ==============================================================================
# SECURITY
# ==============================================================================

def get_secret_key() -> str:
    """Clave secreta para cryptographic."""
    # Si está definida, usarla
    key = os.environ.get('SECRET_KEY')
    if key:
        return key
    
    # Si no, generar una basada en la ruta del proyecto (para desarrollo)
    # NOTA: En producción, esto debe ser una clave real
    root = get_project_root()
    return f"dev-key-{hash(str(root))}"

def get_bcrypt_rounds() -> int:
    """Costo de bcrypt (más alto = más seguro pero más lento)."""
    env = os.environ.get('ENV', 'dev').lower()
    if env == 'prod':
        return 12
    return 4  # Desarrollo rápido

# ==============================================================================
# ENTORNO
# ==============================================================================

def get_env() -> str:
    """Entorno actual: dev, staging, prod."""
    return os.environ.get('ENV', 'dev').lower()

def is_production() -> bool:
    """True si estamos en producción."""
    return get_env() == 'prod'

def is_development() -> bool:
    """True si estamos en desarrollo."""
    return get_env() == 'dev'

# ==============================================================================
# APPLICATION
# ==============================================================================

def get_app_name() -> str:
    """Nombre de la aplicación."""
    return os.environ.get('APP_NAME', 'inventory_system')

def get_app_version() -> str:
    """Versión de la aplicación."""
    return os.environ.get('APP_VERSION', '1.0.0')

# ==============================================================================
# UI
# ==============================================================================

def get_ui_theme() -> str:
    """Tema de UI: light, dark, system."""
    return os.environ.get('UI_THEME', 'system')

def get_ui_language() -> str:
    """Idioma de UI: es, en."""
    return os.environ.get('UI_LANGUAGE', 'es')

# ==============================================================================
# HELPERS
# ==============================================================================

def ensure_directories():
    """Crea los directorios necesarios si no existen."""
    # Directorio de datos
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Directorio de logs
    logs_dir = get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)

def get_config_summary() -> dict:
    """Resumen de la configuración actual."""
    return {
        'app_name': get_app_name(),
        'version': get_app_version(),
        'env': get_env(),
        'db_path': get_db_path(),
        'log_level': get_log_level(),
        'log_file': get_log_file(),
        'ui_theme': get_ui_theme(),
        'ui_language': get_ui_language(),
    }

def print_config():
    """Imprime la configuración actual."""
    print("=== Configuración ===")
    for key, value in get_config_summary().items():
        print(f"  {key}: {value}")
    print("=====================")

# ==============================================================================
# EJEMPLO DE USO
# ==============================================================================
"""
# En tu código:

from src.config import get_database_url, get_log_level, ensure_directories

# Crear directorios al inicio
ensure_directories()

# Usar en config de DB
DATABASE_URL = get_database_url()

# Usar en logger
logging.basicConfig(level=get_log_level())
"""