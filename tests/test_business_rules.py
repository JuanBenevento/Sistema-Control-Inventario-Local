"""Tests para el sistema de reglas de negocio."""

import sys
sys.path.insert(0, '.')

from unittest.mock import Mock
from src.services.business_rules import (
    CannotDeleteSelfRule,
    MustHaveAtLeastOneAdminRule,
    CannotDeleteEntityWithProductsRule,
    CannotDeleteCategoryWithChildrenRule,
    MinimumPasswordLengthRule,
    StockCannotBeNegativeRule,
)


class TestCannotDeleteSelfRule:
    """Tests para CannotDeleteSelfRule."""
    
    def test_no_puede_eliminarse_a_si_mismo(self):
        """Un usuario no puede eliminarse a sí mismo."""
        result = CannotDeleteSelfRule.check(current_user_id=1, user_id_to_delete=1)
        assert result == (False, "No puedes eliminarte a ti mismo")
    
    def test_puede_eliminar_otro_usuario(self):
        """Un usuario puede eliminar a otro."""
        result = CannotDeleteSelfRule.check(current_user_id=1, user_id_to_delete=2)
        assert result == (True, "")


class TestMustHaveAtLeastOneAdminRule:
    """Tests para MustHaveAtLeastOneAdminRule."""
    
    def test_no_puede_eliminar_unico_admin(self):
        """No se puede eliminar el único admin."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        
        result = MustHaveAtLeastOneAdminRule.check(mock_db, user_id_to_delete=1)
        assert result == (False, "No puedes eliminar al único admin del sistema")
    
    def test_puede_eliminar_admin_si_hay_otro(self):
        """Se puede eliminar admin si hay otro activo."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 2
        
        result = MustHaveAtLeastOneAdminRule.check(mock_db, user_id_to_delete=1)
        assert result == (True, "")


class TestCannotDeleteEntityWithProductsRule:
    """Tests para CannotDeleteEntityWithProductsRule."""
    
    def test_no_puede_eliminar_con_productos(self):
        """No se puede eliminar si tiene productos."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        
        result = CannotDeleteEntityWithProductsRule.check(
            mock_db, "category", 1, "category_id"
        )
        assert result[0] == False
        assert "5 producto(s)" in result[1]
    
    def test_puede_eliminar_sin_productos(self):
        """Se puede eliminar si no tiene productos."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        
        result = CannotDeleteEntityWithProductsRule.check(
            mock_db, "category", 1, "category_id"
        )
        assert result == (True, "")


class TestCannotDeleteCategoryWithChildrenRule:
    """Tests para CannotDeleteCategoryWithChildrenRule."""
    
    def test_no_puede_eliminar_con_hijos(self):
        """No se puede eliminar si tiene subcategorías."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        
        result = CannotDeleteCategoryWithChildrenRule.check(mock_db, category_id=1)
        assert result[0] == False
        assert "3 subcategoría(s)" in result[1]
    
    def test_puede_eliminar_sin_hijos(self):
        """Se puede eliminar si no tiene hijos."""
        mock_db = Mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        
        result = CannotDeleteCategoryWithChildrenRule.check(mock_db, category_id=1)
        assert result == (True, "")


class TestMinimumPasswordLengthRule:
    """Tests para MinimumPasswordLengthRule."""
    
    def test_password_muy_corta(self):
        """Password menor a 4 caracteres falla."""
        result = MinimumPasswordLengthRule.check("abc")
        assert result == (False, "La contraseña debe tener al menos 4 caracteres")
    
    def test_password_exacto(self):
        """Password de exactamente 4 caracteres es válido."""
        result = MinimumPasswordLengthRule.check("abcd")
        assert result == (True, "")
    
    def test_password_larga(self):
        """Password larga es válida."""
        result = MinimumPasswordLengthRule.check("password123")
        assert result == (True, "")
    
    def test_password_vacia(self):
        """Password vacía falla."""
        result = MinimumPasswordLengthRule.check("")
        assert result == (False, "La contraseña debe tener al menos 4 caracteres")


class TestStockCannotBeNegativeRule:
    """Tests para StockCannotBeNegativeRule."""
    
    def test_stock_insuficiente_para_salida(self):
        """No puede sacar más de lo que hay."""
        result = StockCannotBeNegativeRule.check(
            current_stock=5, quantity=10, operation="OUT"
        )
        assert result[0] == False
        assert "Stock insuficiente" in result[1]
    
    def test_stock_suficiente_para_salida(self):
        """Puede sacar si hay suficiente."""
        result = StockCannotBeNegativeRule.check(
            current_stock=10, quantity=5, operation="OUT"
        )
        assert result == (True, "")
    
    def test_entrada_no_puede_hacer_negativo(self):
        """Entrada no puede hacer el stock negativo."""
        result = StockCannotBeNegativeRule.check(
            current_stock=5, quantity=-10, operation="IN"
        )
        assert result[0] == False
        assert "negativo" in result[1].lower()
    
    def test_entrada_valida(self):
        """Entrada normal es válida."""
        result = StockCannotBeNegativeRule.check(
            current_stock=5, quantity=10, operation="IN"
        )
        assert result == (True, "")