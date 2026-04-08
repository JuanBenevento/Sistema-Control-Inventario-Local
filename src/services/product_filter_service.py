"""Servicio para filtrado avanzado de productos."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.models.entities import Product, Category, Supplier


class ProductFilterService:
    """Servicio para filtrar productos con múltiples criterios."""

    def __init__(self, db: Session):
        self.db = db
        self.query = db.query(Product)

    def filter_by_text(self, text: str) -> 'ProductFilterService':
        """Filtra por texto en nombre, marca o código."""
        if text and text.strip():
            text = f"%{text.strip()}%"
            self.query = self.query.filter(
                or_(
                    Product.name.ilike(text),
                    Product.brand.ilike(text),
                    Product.barcode.ilike(text)
                )
            )
        return self

    def filter_by_category(self, category_id: Optional[int]) -> 'ProductFilterService':
        """Filtra por categoría. None = todos."""
        if category_id is not None:
            self.query = self.query.filter(Product.category_id == category_id)
        return self

    def filter_by_supplier(self, supplier_id: Optional[int]) -> 'ProductFilterService':
        """Filtra por proveedor. None = todos."""
        if supplier_id is not None:
            self.query = self.query.filter(Product.supplier_id == supplier_id)
        return self

    def filter_by_status(self, status: str) -> 'ProductFilterService':
        """
        Filtra por estado.
        - 'active': solo activos
        - 'inactive': solo inactivos
        - 'all': todos
        """
        if status == 'active':
            self.query = self.query.filter(Product.is_active == True)
        elif status == 'inactive':
            self.query = self.query.filter(Product.is_active == False)
        # 'all' no filtra
        return self

    def filter_by_stock(self, stock_filter: str) -> 'ProductFilterService':
        """
        Filtra por stock.
        - 'all': todos
        - 'low': stock <= min_stock_alert
        - 'out': stock = 0
        - 'available': stock > 0
        """
        if stock_filter == 'low':
            self.query = self.query.filter(
                and_(
                    Product.stock_qty <= Product.min_stock_alert,
                    Product.stock_qty > 0
                )
            )
        elif stock_filter == 'out':
            self.query = self.query.filter(Product.stock_qty == 0)
        elif stock_filter == 'available':
            self.query = self.query.filter(Product.stock_qty > 0)
        # 'all' no filtra
        return self

    def filter_by_price_range(self, min_price: Optional[float], 
                               max_price: Optional[float]) -> 'ProductFilterService':
        """Filtra por rango de precio de venta."""
        if min_price is not None:
            self.query = self.query.filter(Product.sale_price >= min_price)
        if max_price is not None:
            self.query = self.query.filter(Product.sale_price <= max_price)
        return self

    def order_by(self, field: str = 'name', ascending: bool = True) -> 'ProductFilterService':
        """Ordena los resultados."""
        order_func = Product.name
        if field == 'brand':
            order_func = Product.brand
        elif field == 'stock':
            order_func = Product.stock_qty
        elif field == 'price':
            order_func = Product.sale_price
        elif field == 'barcode':
            order_func = Product.barcode
        
        if not ascending:
            order_func = order_func.desc()
        
        self.query = self.query.order_by(order_func)
        return self

    def execute(self) -> List[Product]:
        """Ejecuta la consulta y retorna los resultados."""
        return self.query.all()

    def count(self) -> int:
        """Retorna el conteo de resultados."""
        return self.query.count()