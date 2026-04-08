from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import get_database_url, get_db_echo, ensure_directories

# Crear directorios necesarios al importar
ensure_directories()

# Usar configuración centralizada
DATABASE_URL = get_database_url()
ECHO_SQL = get_db_echo()

# El engine gestiona la conexión física
engine = create_engine(DATABASE_URL, echo=ECHO_SQL)

# SessionLocal es nuestra fábrica de conexiones (EntityManager)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase madre de todas las entidades
Base = declarative_base()

def init_db():
    # Importamos las entidades aquí para evitar importaciones circulares
    import src.models.entities 
    Base.metadata.create_all(bind=engine)