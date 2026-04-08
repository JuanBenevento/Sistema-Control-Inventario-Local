"""Servicio para gestión de usuarios."""
from sqlalchemy.orm import Session
from src.models.entities import User
from src.repository.user_repository import UserRepository
from src.services.business_rules import (
    CannotDeleteSelfRule,
    MustHaveAtLeastOneAdminRule,
    MinimumPasswordLengthRule,
)


class UserService:
    """Servicio para operaciones de usuarios."""

    def __init__(self, current_user_id: int = None):
        self._current_user_id = current_user_id

    def create(self, db: Session, username: str, password: str, 
               full_name: str = None, role: str = 'vendedor') -> tuple:
        """Crea un nuevo usuario."""
        existing = UserRepository.get_by_username(db, username)
        if existing:
            return None, "El usuario ya existe"
        
        valid, error = MinimumPasswordLengthRule.check(password)
        if not valid:
            return None, error
        
        user = User(
            username=username,
            full_name=full_name,
            role=role,
            is_admin=role == 'admin',
            is_active=True
        )
        user.set_password(password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user, None

    def update(self, db: Session, user_id: int, **fields) -> tuple:
        """Actualiza un usuario."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None, "Usuario no encontrado"
        
        if 'password' in fields and fields['password']:
            valid, error = MinimumPasswordLengthRule.check(fields['password'])
            if not valid:
                return None, error
        
        for key, value in fields.items():
            if key == 'role':
                user.role = value
                user.is_admin = (value == 'admin')
            elif key == 'password' and value:
                user.set_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        
        return user, None

    def delete(self, db: Session, user_id: int) -> tuple:
        """Elimina un usuario (borrado lógico)."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return False, "Usuario no encontrado"
        
        if self._current_user_id:
            valid, error = CannotDeleteSelfRule.check(self._current_user_id, user_id)
            if not valid:
                return False, error
        
        valid, error = MustHaveAtLeastOneAdminRule.check(db, user_id)
        if not valid:
            return False, error
        
        user.is_active = False
        db.commit()
        
        return True, None

    def get_all(self, db: Session, include_inactive: bool = False) -> list:
        """Obtiene todos los usuarios."""
        query = db.query(User)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return query.order_by(User.username).all()

    def get_by_id(self, db: Session, user_id: int):
        """Obtiene un usuario por ID."""
        return UserRepository.get_by_id(db, user_id)