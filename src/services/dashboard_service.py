"""
Servicio para el Dashboard de KPIs.
"""
from datetime import datetime, timedelta
from src.database.config import SessionLocal
from src.repository.sales_repository import SalesRepository


class DashboardService:
    """Servicio para obtener métricas del dashboard."""

    @staticmethod
    def get_daily_sales() -> dict:
        """Ventas de hoy."""
        db = SessionLocal()
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            return SalesRepository.get_sales_by_period(db, today, tomorrow)
        finally:
            db.close()

    @staticmethod
    def get_weekly_sales() -> dict:
        """Ventas de los últimos 7 días."""
        db = SessionLocal()
        try:
            end = datetime.utcnow()
            start = end - timedelta(days=7)
            return SalesRepository.get_sales_by_period(db, start, end)
        finally:
            db.close()

    @staticmethod
    def get_monthly_sales() -> dict:
        """Ventas del mes actual."""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = now.replace(year=now.year + 1, month=1, day=1)
            else:
                end = now.replace(month=now.month + 1, day=1)
            return SalesRepository.get_sales_by_period(db, start, end)
        finally:
            db.close()

    @staticmethod
    def get_low_stock_alerts(limit: int = 10) -> list:
        """Productos bajo stock."""
        db = SessionLocal()
        try:
            return SalesRepository.get_low_stock_products(db, limit)
        finally:
            db.close()

    @staticmethod
    def get_top_selling_products(limit: int = 5, days: int = 30) -> list:
        """Productos más vendidos."""
        db = SessionLocal()
        try:
            return SalesRepository.get_top_products(db, limit, days)
        finally:
            db.close()

    @staticmethod
    def get_margin_summary() -> dict:
        """Resumen de márgenes."""
        db = SessionLocal()
        try:
            return SalesRepository.get_margin_summary(db)
        finally:
            db.close()