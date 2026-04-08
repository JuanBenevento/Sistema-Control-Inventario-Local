"""
Sistema de permisos basado en permisos, no en roles.
"""
from functools import wraps
from typing import Set

PERMISSIONS = {
    'product.create', 'product.read', 'product.update', 'product.delete',
    'category.create', 'category.read', 'category.update', 'category.delete',
    'supplier.create', 'supplier.read', 'supplier.update', 'supplier.delete',
    'stock.in', 'stock.out', 'stock.read',
    'report.view_dashboard', 'report.export',
    'user.manage', 'user.read',
}

ROLES = {
    'admin': set(PERMISSIONS),
    'vendedor': {
        'product.create', 'product.read', 'product.update', 'product.delete',
        'category.create', 'category.read', 'category.update', 'category.delete',
        'supplier.create', 'supplier.read', 'supplier.update', 'supplier.delete',
        'stock.in', 'stock.out', 'stock.read',
        'report.view_dashboard', 'report.export',
        'user.read',
    },
}


class PermissionError(Exception):
    pass


def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'check_permission'):
                return func(self, *args, **kwargs)
            
            if not self.check_permission(permission):
                raise PermissionError(f"No tienes permiso para: {permission}")
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def has_permission(user_permissions: Set[str], required: str) -> bool:
    return required in user_permissions