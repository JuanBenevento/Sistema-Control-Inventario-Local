"""Servicio para gestión de proveedores."""
from typing import List
from sqlalchemy.orm import Session
from src.repository.supplier_repository import SupplierRepository


class SupplierService:
    """Servicio para operaciones de proveedores."""

    def __init__(self, user_permissions: set = None):
        """
        Inicializa el servicio.
        
        Args:
            user_permissions: Conjunto de permisos del usuario actual.
                             Si es None, se permiten todas las operaciones.
        """
        self._permissions = user_permissions or set()

    def check_permission(self, permission: str) -> bool:
        """Verifica si el usuario tiene el permiso."""
        return permission in self._permissions or len(self._permissions) == 0

    def _verify_permission(self, permission: str):
        """Lanza excepción si no tiene permiso."""
        from src.models.permissions import PermissionError
        if not self.check_permission(permission):
            raise PermissionError(f"No tienes permiso para: {permission}")

    def get_all(self, db: Session, include_inactive: bool = False) -> List:
        """Obtiene todos los proveedores."""
        self._verify_permission('supplier.read')
        return SupplierRepository.get_all(db, include_inactive)

    def get_by_id(self, db: Session, supplier_id: int):
        """Obtiene un proveedor por ID."""
        self._verify_permission('supplier.read')
        return SupplierRepository.get_by_id(db, supplier_id)

    def search(self, db: Session, term: str) -> List:
        """Busca proveedores."""
        self._verify_permission('supplier.read')
        return SupplierRepository.search(db, term)

    def create(self, db: Session, name: str, contact_name: str = None,
               phone: str = None, email: str = None,
               address: str = None, notes: str = None):
        """Crea un nuevo proveedor."""
        self._verify_permission('supplier.create')
        
        existing = SupplierRepository.get_by_name(db, name)
        if existing:
            return None, f"Ya existe un proveedor con el nombre '{name}'"
        
        supplier = SupplierRepository.create(
            db, name, contact_name, phone, email, address, notes
        )
        return supplier, None

    def update(self, db: Session, supplier_id: int, **fields):
        """Actualiza un proveedor."""
        self._verify_permission('supplier.update')
        
        supplier = SupplierRepository.get_by_id(db, supplier_id)
        if not supplier:
            return None, "Proveedor no encontrado"
        
        if 'name' in fields:
            existing = SupplierRepository.get_by_name(db, fields['name'])
            if existing and existing.id != supplier_id:
                return None, f"Ya existe un proveedor con el nombre '{fields['name']}'"
        
        updated = SupplierRepository.update(db, supplier_id, **fields)
        return updated, None

    def delete(self, db: Session, supplier_id: int) -> tuple:
        """Elimina un proveedor."""
        self._verify_permission('supplier.delete')
        
        supplier = SupplierRepository.get_by_id(db, supplier_id)
        if not supplier:
            return False, "Proveedor no encontrado"
        
        if SupplierRepository.has_products(db, supplier_id):
            return False, "No se puede eliminar: tiene productos asociados"
        
        success = SupplierRepository.delete(db, supplier_id)
        return success, None