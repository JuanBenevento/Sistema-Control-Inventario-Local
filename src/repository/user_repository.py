from sqlalchemy.orm import Session
from src.models.entities import User
from src.utils.logger import get_logger
from src.utils.auth import migrate_to_bcrypt

logger = get_logger(__name__)


class UserRepository:
    """Repository para operaciones de usuarios."""

    @staticmethod
    def get_by_username(db: Session, username: str):
        """Obtiene un usuario por nombre de usuario."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int):
        """Obtiene un usuario por ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, username: str, password: str, full_name: str = None, is_admin: bool = False):
        """Crea un nuevo usuario."""
        user = User(
            username=username,
            full_name=full_name,
            is_admin=is_admin
        )
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str):
        """Autentica un usuario. Retorna el usuario si es válido, None si no."""
        user = UserRepository.get_by_username(db, username)
        if user and user.is_active:
            is_valid, needs_migration = user.check_password(password)
            if is_valid:
                if needs_migration:
                    user.set_password(password)
                    db.commit()
                    logger.info(f"Usuario migrado a bcrypt: {username}")
                logger.info(f"Login exitoso: {username}")
                return user
        if user:
            logger.warning(f"Login fallido: usuario={username}")
        return None

    @staticmethod
    def get_all(db: Session):
        """Obtiene todos los usuarios activos."""
        return db.query(User).filter(User.is_active == True).all()
