"""Servicio para gestión de categorías."""
from typing import List
from sqlalchemy.orm import Session
from src.repository.category_repository import CategoryRepository
from src.models.permissions import PermissionError


class CategoryService:
    """Servicio para operaciones de categorías."""

    def __init__(self, user_permissions: set = None):
        """
        Inicializa el servicio.
        
        Args:
            user_permissions: Conjunto de permisos del usuario actual.
                             Si es None, se permiten todas las operaciones (admin).
        """
        self._permissions = user_permissions or set()

    def check_permission(self, permission: str) -> bool:
        """Verifica si el usuario tiene el permiso."""
        return permission in self._permissions or len(self._permissions) == 0

    def _verify_permission(self, permission: str):
        """Lanza excepción si no tiene permiso."""
        if not self.check_permission(permission):
            raise PermissionError(f"No tienes permiso para: {permission}")

    def get_all(self, db: Session, include_inactive: bool = False) -> List:
        """Obtiene todas las categorías."""
        self._verify_permission('category.read')
        return CategoryRepository.get_all(db, include_inactive)

    def get_by_id(self, db: Session, category_id: int):
        """Obtiene una categoría por ID."""
        self._verify_permission('category.read')
        return CategoryRepository.get_by_id(db, category_id)

    def get_root_categories(self, db: Session) -> List:
        """Obtiene categorías de nivel superior."""
        self._verify_permission('category.read')
        return CategoryRepository.get_root_categories(db)

    def get_children(self, db: Session, parent_id: int) -> List:
        """Obtiene subcategorías."""
        self._verify_permission('category.read')
        return CategoryRepository.get_children(db, parent_id)

    def get_all_with_hierarchy(self, db: Session) -> List:
        """
        Obtiene todas las categorías organizadas jerárquicamente.
        Retorna lista de tuplas (category, level, display_name).
        """
        self._verify_permission('category.read')
        
        all_categories = CategoryRepository.get_all(db)
        result = []
        
        def add_with_children(parent_id, level):
            for cat in all_categories:
                if cat.parent_id == parent_id:
                    indent = "  " * level
                    result.append((cat, level, f"{indent}{cat.name}"))
                    add_with_children(cat.id, level + 1)
        
        add_with_children(None, 0)
        return result

    def create(self, db: Session, name: str, description: str = None,
               parent_id: int = None):
        """Crea una nueva categoría."""
        self._verify_permission('category.create')
        
        existing = CategoryRepository.get_by_name(db, name)
        if existing:
            return None, f"Ya existe una categoría con el nombre '{name}'"
        
        if parent_id:
            parent = CategoryRepository.get_by_id(db, parent_id)
            if not parent:
                return None, "Categoría padre no encontrada"
        
        category = CategoryRepository.create(db, name, description, parent_id)
        return category, None

    def update(self, db: Session, category_id: int, **fields):
        """Actualiza una categoría."""
        self._verify_permission('category.update')
        
        category = CategoryRepository.get_by_id(db, category_id)
        if not category:
            return None, "Categoría no encontrada"
        
        if 'name' in fields:
            existing = CategoryRepository.get_by_name(db, fields['name'])
            if existing and existing.id != category_id:
                return None, f"Ya existe una categoría con el nombre '{fields['name']}'"
        
        updated = CategoryRepository.update(db, category_id, **fields)
        return updated, None

    def delete(self, db: Session, category_id: int) -> tuple:
        """Elimina una categoría."""
        self._verify_permission('category.delete')
        
        category = CategoryRepository.get_by_id(db, category_id)
        if not category:
            return False, "Categoría no encontrada"
        
        if category.name == "Sin Categoría":
            return False, "No se puede eliminar la categoría 'Sin Categoría'"
        
        if CategoryRepository.has_children(db, category_id):
            return False, "No se puede eliminar: tiene subcategorías"
        
        if CategoryRepository.has_products(db, category_id):
            return False, "No se puede eliminar: tiene productos asociados"
        
        success = CategoryRepository.delete(db, category_id)
        return success, None

    def get_or_create_default(self, db: Session):
        """Obtiene o crea la categoría por defecto."""
        return CategoryRepository.get_or_create_default(db)