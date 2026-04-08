"""Tests básicos para servicios del proyecto."""

import sys
sys.path.insert(0, '.')


def test_import_services():
    """Verifica que los servicios pueden ser importados correctamente."""
    from src.services.product_service import ProductService
    from src.services.stock_service import StockService
    assert ProductService is not None
    assert StockService is not None


def test_import_repositories():
    """Verifica que los repositorios pueden ser importados correctamente."""
    from src.repository.product_repository import ProductRepository
    from src.repository.user_repository import UserRepository
    assert ProductRepository is not None
    assert UserRepository is not None


def test_import_models():
    """Verifica que los modelos pueden ser importados correctamente."""
    from src.models.entities import Product, User, StockMovement
    assert Product is not None
    assert User is not None
    assert StockMovement is not None