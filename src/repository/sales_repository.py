"""
Repository para consultas agregadas de ventas y métricas.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from src.models.entities import Product, StockMovement


class SalesRepository:
    """Repository para métricas y reportes."""

    @staticmethod
    def get_sales_by_period(db: Session, start_date: datetime, end_date: datetime) -> dict:
        """
        Obtiene ventas (movimientos OUT) en un período.
        
        Returns:
            dict con 'count' (número de ventas) y 'total' (suma de importe estimado)
        """
        movements = db.query(StockMovement).filter(
            StockMovement.type == 'OUT',
            StockMovement.created_at >= start_date,
            StockMovement.created_at <= end_date
        ).all()
        
        # Calcular total estimado (cantidad * precio_venta del producto)
        total = 0
        for m in movements:
            product = db.get(Product, m.product_id)
            if product and product.sale_price:
                total += m.quantity * product.sale_price
        
        return {
            'count': len(movements),
            'total': total
        }

    @staticmethod
    def get_low_stock_products(db: Session, limit: int = 10) -> list:
        """
        Obtiene productos con stock bajo o igual al umbral.
        """
        return db.query(Product).filter(
            Product.is_active == True,
            Product.stock_qty <= Product.min_stock_alert
        ).order_by(Product.stock_qty.asc()).limit(limit).all()

    @staticmethod
    def get_top_products(db: Session, limit: int = 5, days: int = 30) -> list:
        """
        Obtiene productos más vendidos en los últimos N días.
        
        Returns:
            Lista de tuplas (product, total_quantity)
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            StockMovement.product_id,
            func.sum(StockMovement.quantity).label('total')
        ).filter(
            StockMovement.type == 'OUT',
            StockMovement.created_at >= start_date
        ).group_by(StockMovement.product_id).order_by(
            func.sum(StockMovement.quantity).desc()
        ).limit(limit).all()
        
        top_products = []
        for r in results:
            product = db.get(Product, r.product_id)
            if product:
                top_products.append((product, r.total))
        
        return top_products

    @staticmethod
    def get_margin_summary(db: Session) -> dict:
        """
        Obtiene resumen de márgenes de ganancia.
        """
        products = db.query(Product).filter(
            Product.is_active == True,
            Product.sale_price > 0,
            Product.cost_usd > 0
        ).all()
        
        if not products:
            return {'average': 0, 'count': 0}
        
        total_margin = sum(p.margin_percentage for p in products)
        return {
            'average': round(total_margin / len(products), 2),
            'count': len(products)
        }