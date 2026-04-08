"""
Sistema de reglas de negocio.
Cada regla es una clase con método check() que retorna (bool, str).
"""
from typing import Tuple


class BusinessRule:
    """
    Clase base para reglas de negocio.
    Cada regla debe implementar check().
    """
    name: str = "business_rule"
    
    @classmethod
    def check(cls, *args, **kwargs) -> Tuple[bool, str]:
        """
        Verifica si la regla se cumple.
        
        Returns:
            Tuple[bool, str]: (cumple, mensaje_error)
        """
        raise NotImplementedError


class CannotDeleteSelfRule(BusinessRule):
    """Regla: Un usuario no puede eliminarse a sí mismo."""
    name = "cannot_delete_self"
    
    @classmethod
    def check(cls, current_user_id: int, user_id_to_delete: int) -> Tuple[bool, str]:
        if current_user_id == user_id_to_delete:
            return False, "No puedes eliminarte a ti mismo"
        return True, ""


class MustHaveAtLeastOneAdminRule(BusinessRule):
    """Regla: Siempre debe existir al menos un admin activo."""
    name = "must_have_at_least_one_admin"
    
    @classmethod
    def check(cls, db, user_id_to_delete: int) -> Tuple[bool, str]:
        from src.models.entities import User
        
        admin_count = db.query(User).filter(
            User.role == 'admin',
            User.is_active == True,
            User.id != user_id_to_delete
        ).count()
        
        if admin_count == 0:
            return False, "No puedes eliminar al único admin del sistema"
        
        return True, ""


class CannotDeleteEntityWithProductsRule(BusinessRule):
    """Regla: No se puede eliminar una entidad que tiene productos asociados."""
    name = "cannot_delete_with_products"
    
    @classmethod
    def check(cls, db, entity_type: str, entity_id: int, product_field: str) -> Tuple[bool, str]:
        from src.models.entities import Product
        
        filter_kwargs = {product_field: entity_id}
        product_count = db.query(Product).filter(**filter_kwargs).count()
        
        if product_count > 0:
            return False, f"No se puede eliminar: tiene {product_count} producto(s) asociado(s)"
        
        return True, ""


class CannotDeleteCategoryWithChildrenRule(BusinessRule):
    """Regla: No se puede eliminar una categoría que tiene subcategorías."""
    name = "cannot_delete_with_children"
    
    @classmethod
    def check(cls, db, category_id: int) -> Tuple[bool, str]:
        from src.models.entities import Category
        
        child_count = db.query(Category).filter(
            Category.parent_id == category_id,
            Category.is_active == True
        ).count()
        
        if child_count > 0:
            return False, f"No se puede eliminar: tiene {child_count} subcategoría(s)"
        
        return True, ""


class MinimumPasswordLengthRule(BusinessRule):
    """Regla: La contraseña debe tener un largo mínimo."""
    name = "minimum_password_length"
    MIN_LENGTH = 4
    
    @classmethod
    def check(cls, password: str) -> Tuple[bool, str]:
        if not password or len(password) < cls.MIN_LENGTH:
            return False, f"La contraseña debe tener al menos {cls.MIN_LENGTH} caracteres"
        return True, ""


class StockCannotBeNegativeRule(BusinessRule):
    """Regla: El stock no puede ser negativo."""
    name = "stock_cannot_be_negative"
    
    @classmethod
    def check(cls, current_stock: int, quantity: int, operation: str) -> Tuple[bool, str]:
        if operation == "OUT" and current_stock < quantity:
            return False, f"Stock insuficiente: {current_stock} disponible(s), {quantity} solicitado(s)"
        if current_stock + quantity < 0:
            return False, "El stock no puede ser negativo"
        return True, ""