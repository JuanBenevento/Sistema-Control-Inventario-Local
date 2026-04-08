from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.config import Base
from typing import Tuple
import hashlib

class User(Base):
    """Usuario del sistema con autenticación."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(64), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(20), default='vendedor')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str):
        """Genera hash bcrypt de la contraseña."""
        from src.utils.auth import hash_password
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> Tuple[bool, bool]:
        """Verifica la contraseña."""
        from src.utils.auth import verify_password
        return verify_password(password, self.password_hash)


class Category(Base):
    """Categoría de productos con soporte para subcategorías."""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    stock_qty = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    sale_price = Column(Float, default=0.0)
    min_stock_alert = Column(Integer, default=2)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    movements = relationship("StockMovement", back_populates="product")
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")

    @property
    def margin_percentage(self):
        """Calcula el porcentaje de margen de ganancia."""
        if self.sale_price and self.sale_price > 0 and self.cost_usd:
            return ((self.sale_price - self.cost_usd) / self.sale_price) * 100
        return 0.0

class StockMovement(Base):
    __tablename__ = 'stock_movements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    type = Column(String) # 'IN' o 'OUT'
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="movements")


class Supplier(Base):
    """Proveedor de productos."""
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    contact_name = Column(String(100))
    phone = Column(String(30))
    email = Column(String(100))
    address = Column(String(255))
    notes = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = relationship("Product", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"