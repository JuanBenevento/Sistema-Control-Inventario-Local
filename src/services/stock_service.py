from src.repository.product_repository import ProductRepository
from src.repository.stock_movement_repository import StockMovementRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StockService:
    """Service layer for stock movement operations."""

    @staticmethod
    def record_in(db, product_id, quantity, user_name=None):
        """
        Records a stock IN movement.
        
        Args:
            db: SQLAlchemy session
            product_id: Product ID
            quantity: Quantity to add (positive integer)
            user_name: Username for audit trail
        
        Returns:
            Updated Product instance
        
        Raises:
            ValueError: If quantity is not positive or product not found
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        
        result = ProductRepository.update_stock(
            db=db,
            product_id=product_id,
            quantity=quantity,
            move_type='IN',
            user_name=user_name
        )
        logger.info(f"Movimiento IN: producto_id={product_id}, cantidad={quantity}, usuario={user_name}")
        return result

    @staticmethod
    def record_out(db, product_id, quantity, user_name=None):
        """
        Records a stock OUT movement.
        
        Args:
            db: SQLAlchemy session
            product_id: Product ID
            quantity: Quantity to remove (positive integer)
            user_name: Username for audit trail
        
        Returns:
            Updated Product instance
        
        Raises:
            ValueError: If quantity is not positive, product not found, or insufficient stock
        """
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        
        result = ProductRepository.update_stock(
            db=db,
            product_id=product_id,
            quantity=quantity,
            move_type='OUT',
            user_name=user_name
        )
        logger.info(f"Movimiento OUT: producto_id={product_id}, cantidad={quantity}, usuario={user_name}")
        return result

    @staticmethod
    def get_product_movements(db, product_id):
        """
        Gets all stock movements for a product.
        
        Args:
            db: SQLAlchemy session
            product_id: Product ID
        
        Returns:
            List of StockMovement instances, ordered by timestamp (most recent first)
        """
        return StockMovementRepository.get_by_product(db, product_id)

    @staticmethod
    def calculate_available(product):
        """
        Returns the current available stock for a product.
        
        Args:
            product: Product instance
        
        Returns:
            Current stock quantity (int)
        """
        return product.stock_qty if product else 0