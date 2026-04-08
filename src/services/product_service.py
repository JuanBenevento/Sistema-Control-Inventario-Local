from src.repository.product_repository import ProductRepository


class ProductService:
    """Service layer for product operations."""

    @staticmethod
    def create_product(db, barcode, name, brand, cost_usd, sale_price, initial_stock=0, min_stock_alert=2, category_id=None, supplier_id=None):
        """
        Creates a product with margin calculation.
        
        Args:
            db: SQLAlchemy session
            barcode: Product barcode
            name: Product name
            brand: Brand name
            cost_usd: Cost in USD
            sale_price: Sale price
            initial_stock: Initial stock quantity (default: 0)
            min_stock_alert: Minimum stock alert threshold (default: 2)
            category_id: Category ID (optional)
            supplier_id: Supplier ID (optional)
        
        Returns:
            Created Product instance
        """
        return ProductRepository.create_product(
            db=db,
            barcode=barcode,
            name=name,
            brand=brand,
            cost_usd=cost_usd,
            sale_price=sale_price,
            initial_stock=initial_stock,
            min_stock_alert=min_stock_alert,
            category_id=category_id,
            supplier_id=supplier_id,
        )

    @staticmethod
    def get_by_barcode(db, barcode, only_active=True):
        """
        Gets a product by barcode.
        
        Args:
            db: SQLAlchemy session
            barcode: Product barcode
            only_active: If False, returns inactive products too
        
        Returns:
            Product instance or None if not found
        """
        if only_active:
            return ProductRepository.get_by_barcode(db, barcode)
        else:
            return ProductRepository.get_by_barcode_any_status(db, barcode)

    @staticmethod
    def get_product(db, product_id):
        """
        Gets a single product by ID.
        
        Args:
            db: SQLAlchemy session
            product_id: Product ID
        
        Returns:
            Product instance or None if not found
        """
        return ProductRepository.get_by_id(db, product_id)

    @staticmethod
    def get_all_products(db):
        """
        Gets all products.
        
        Args:
            db: SQLAlchemy session
        
        Returns:
            List of Product instances
        """
        return ProductRepository.get_all(db)

    @staticmethod
    def update_product(db, product_id, **fields):
        """
        Updates product fields.
        
        Args:
            db: SQLAlchemy session
            product_id: Product ID
            **fields: Fields to update (e.g., name='New Name', sale_price=100.0)
        
        Returns:
            Updated Product instance or None if not found
        """
        return ProductRepository.update(db, product_id, **fields)

    @staticmethod
    def deactivate(db, product_id):
        """
        Da de baja un producto. Solo si stock = 0.
        
        Returns:
            tuple: (product, error_message)
        """
        return ProductRepository.deactivate(db, product_id)

    @staticmethod
    def activate(db, product_id):
        """
        Reactiva un producto. Solo si stock > 0.
        
        Returns:
            tuple: (product, error_message)
        """
        return ProductRepository.activate(db, product_id)

    @staticmethod
    def get_margin(product):
        """
        Calculates profit margin percentage.
        
        Formula: (sale_price - cost_usd) / sale_price * 100
        
        Args:
            product: Product instance
        
        Returns:
            Margin as percentage (float), or 0.0 if sale_price is 0
        """
        if product.sale_price is None or product.sale_price == 0:
            return 0.0
        
        margin = (product.sale_price - product.cost_usd) / product.sale_price * 100
        return round(margin, 2)