from sqlalchemy.orm import Session
from src.models.entities import Product


# Whitelist de campos permitidos para actualización
ALLOWED_UPDATE_FIELDS = {
    'name', 'brand', 'barcode', 'cost_usd', 'sale_price',
    'stock_qty', 'min_stock_alert', 'is_active',
    'category_id', 'supplier_id'
}


class ProductRepository:
    @staticmethod
    def get_by_barcode(db: Session, barcode: str, only_active: bool = True):
        """Busca producto por barcode. Por defecto solo activos."""
        query = db.query(Product).filter(Product.barcode == barcode)
        if only_active:
            query = query.filter(Product.is_active == True)
        return query.first()
    
    @staticmethod
    def get_by_barcode_any_status(db: Session, barcode: str):
        """Busca producto por barcode sin importar estado (activo o no)."""
        return db.query(Product).filter(Product.barcode == barcode).first()

    @staticmethod
    def get_by_id(db: Session, product_id: int):
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_all(db: Session, only_active: bool = True):
        """Obtiene todos los productos. Por defecto solo activos."""
        query = db.query(Product)
        if only_active:
            query = query.filter(Product.is_active == True)
        return query.order_by(Product.name).all()

    @staticmethod
    def get_inactive(db: Session):
        """Obtiene productos dados de baja."""
        return db.query(Product).filter(Product.is_active == False).order_by(Product.name).all()

    @staticmethod
    def update(db: Session, product_id: int, **fields):
        """Update product fields. Returns updated product or None if not found.
        
        Only fields in ALLOWED_UPDATE_FIELDS can be updated (whitelist).
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return None
        
        # Filtrar solo campos permitidos (whitelist)
        allowed = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
        
        for key, value in allowed.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update_stock(db: Session, product_id: int, quantity: int, move_type: str, user_name: str | None = None):
        if move_type not in ('IN', 'OUT'):
            raise ValueError("move_type must be 'IN' or 'OUT'")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        from src.models.entities import StockMovement
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return None
        
        current_qty: int = product.stock_qty  # type: ignore[assignment]
        delta = quantity if move_type == 'IN' else -quantity
        new_qty = current_qty + delta
        
        if new_qty < 0:
            raise ValueError(f"Insufficient stock. Available: {product.stock_qty}, requested: {quantity}")

        db.query(Product).filter(Product.id == product_id).update(
            {"stock_qty": new_qty}
        )

        movement = StockMovement(
            product_id=product_id,
            type=move_type,
            quantity=quantity,
            user_name=user_name
        )

        db.add(movement)
        db.commit()
        
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def deactivate(db: Session, product_id: int):
        """Da de baja un producto. Solo si stock = 0."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return None, "Producto no encontrado"
        
        if product.stock_qty > 0:
            return None, f"No se puede dar de baja. Stock actual: {product.stock_qty}"
        
        product.is_active = False
        db.commit()
        db.refresh(product)
        return product, None

    @staticmethod
    def activate(db: Session, product_id: int):
        """Reactiva un producto. Solo si stock > 0."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return None, "Producto no encontrado"
        
        if product.stock_qty <= 0:
            return None, "No se puede dar de alta. Stock es 0."
        
        product.is_active = True
        db.commit()
        db.refresh(product)
        return product, None

    @staticmethod
    def create_product(db: Session, barcode: str, name: str, brand: str, 
                      initial_stock: int, cost_usd: float, sale_price: float = 0.0,
                      min_stock_alert: int = 2, category_id: int = None,
                      supplier_id: int = None):
        """Crea un nuevo producto activo con stock inicial opcional."""
        from src.models.entities import StockMovement
        
        new_product = Product(
            barcode=barcode,
            name=name,
            brand=brand,
            stock_qty=initial_stock,
            cost_usd=cost_usd,
            sale_price=sale_price,
            min_stock_alert=min_stock_alert,
            is_active=True,
            category_id=category_id,
            supplier_id=supplier_id,
        )
        db.add(new_product)
        
        # Si hay stock inicial, registrar el movimiento
        if initial_stock > 0:
            movement = StockMovement(
                product_id=None,  # Se asigna después del flush
                type="IN",
                quantity=initial_stock,
                user_name="Sistema"
            )
            db.flush()  # Obtener el ID del producto
            movement.product_id = new_product.id
            db.add(movement)
        
        db.commit()
        db.refresh(new_product)
        return new_product
