from sqlalchemy.orm import Session
from src.models.entities import StockMovement


class StockMovementRepository:
    """Repository for stock movement operations."""

    @staticmethod
    def get_by_product(db: Session, product_id: int):
        """Get all movements for a specific product, ordered by created_at descending."""
        return db.query(StockMovement).filter(
            StockMovement.product_id == product_id
        ).order_by(StockMovement.created_at.desc()).all()

    @staticmethod
    def create(db: Session, product_id: int, movement_type: str, quantity: int, user_name: str | None = None):
        """Create a new stock movement record."""
        movement = StockMovement(
            product_id=product_id,
            type=movement_type,
            quantity=quantity,
            user_name=user_name
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement