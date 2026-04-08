"""
Configuración centralizada de logging.
=========================================
Usa variables de entorno de src/config.py

Características:
- Formato legible para desarrollo
- Formato JSON para producción
- Contexto enriquecido (filename, function, line)
- Colores en consola (development)
- Rotación de logs (producción)
"""
import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from src.config import get_log_file, get_log_level, get_log_rotation, get_env, get_app_name, get_app_version

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

LOG_FILE = get_log_file()
LOG_LEVEL = get_log_level()
LOG_DIR = Path(LOG_FILE).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5 if get_log_rotation() else 1
ENV = get_env()

# Colores para terminal (solo en dev)
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

# Mapeo nivel -> color
LEVEL_COLORS = {
    'DEBUG': Colors.CYAN,
    'INFO': Colors.GREEN,
    'WARNING': Colors.YELLOW,
    'ERROR': Colors.RED,
    'CRITICAL': Colors.MAGENTA + Colors.BOLD,
}

# ==============================================================================
# FORMATTERS
# ==============================================================================

class ColoredFormatter(logging.Formatter):
    """Formatter con colores para desarrollo."""
    
    def format(self, record):
        # Color según nivel
        color = LEVEL_COLORS.get(record.levelname, Colors.RESET)
        
        # Mensaje formateada
        msg = super().format(record)
        
        # Agregar color
        if sys.stderr.isatty():
            return f"{color}{msg}{Colors.RESET}"
        return msg


class JsonFormatter(logging.Formatter):
    """Formatter JSON para producción."""
    
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "app": get_app_name(),
            "version": get_app_version(),
            "env": ENV,
        }, ensure_ascii=False)


# ==============================================================================
# HANDLERS
# ==============================================================================

def _create_file_handler():
    """Crea el handler de archivo."""
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    
    if ENV == 'prod':
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
    
    return handler


def _create_console_handler():
    """Crea el handler de consola."""
    handler = logging.StreamHandler(sys.stderr)
    
    if ENV == 'prod':
        # Producción: solo warnings+ en consola
        handler.setLevel(logging.WARNING)
        handler.setFormatter(JsonFormatter())
    else:
        # Desarrollo: todo con colores
        handler.setLevel(logging.DEBUG)
        formatter = ColoredFormatter(
            '%(levelname)-8s | %(message)s'
        )
        handler.setFormatter(formatter)
    
    return handler


# ==============================================================================
# GET LOGGER
# ==============================================================================

_loggers = {}  # Cache de loggers

def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado.
    
    Args:
        name: Nombre del logger (usualmente __name__)
        
    Returns:
        Logger configurado
    """
    # Retornar si ya existe
    if name in _loggers:
        return _loggers[name]
    
    # Crear logger
    logger = logging.getLogger(name)
    
    # Ya tiene handlers
    if logger.handlers:
        _loggers[name] = logger
        return logger
    
    # Nivel desde config
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    
    # Agregar handlers
    logger.addHandler(_create_file_handler())
    logger.addHandler(_create_console_handler())
    
    # Cache
    _loggers[name] = logger
    
    return logger


# ==============================================================================
# LOGGERS PREDEFINIDOS
# ==============================================================================

# Logger raíz para la app
app_logger = get_logger(get_app_name())

# ==============================================================================
# EJEMPLO DE USO
# ==============================================================================
"""
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Debug info")      # Solo en dev
logger.info("Información")      # Normal
logger.warning("Advertencia")   # Problema menor
logger.error("Error")           # Problema mayor
logger.critical("Crítico")      # Fallo completo
"""