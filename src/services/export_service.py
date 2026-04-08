"""
Servicio para exportar datos a CSV/Excel.
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


class ExportService:
    """Servicio para exportar datos."""

    @staticmethod
    def export_inventory(db, filepath: str, format: str = 'csv') -> bool:
        """
        Exporta el inventario completo a CSV o Excel.
        
        Args:
            db: Sesión de base de datos
            filepath: Ruta del archivo de destino
            format: 'csv' o 'excel'
        
        Returns:
            True si fue exitoso
        """
        from src.models.entities import Product
        
        products = db.query(Product).filter(
            Product.is_active == True
        ).order_by(Product.name).all()
        
        data = []
        for p in products:
            data.append({
                'Código': p.barcode,
                'Nombre': p.name,
                'Marca': p.brand or '',
                'Stock': p.stock_qty,
                'Costo (USD)': p.cost_usd,
                'Precio Venta (USD)': p.sale_price,
                'Margen (%)': p.margin_percentage,
                'Stock Mínimo': p.min_stock_alert,
                'Estado': 'Activo'
            })
        
        df = pd.DataFrame(data)
        
        if format == 'csv':
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(filepath, index=False, sheet_name='Inventario')
        
        return True

    @staticmethod
    def export_movements(db, filepath: str, format: str = 'csv',
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> bool:
        """
        Exporta historial de movimientos a CSV o Excel.
        
        Args:
            db: Sesión de base de datos
            filepath: Ruta del archivo de destino
            format: 'csv' o 'excel'
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
        
        Returns:
            True si fue exitoso
        """
        from src.models.entities import StockMovement, Product
        
        query = db.query(StockMovement).join(Product)
        
        if start_date:
            query = query.filter(StockMovement.created_at >= start_date)
        if end_date:
            query = query.filter(StockMovement.created_at <= end_date)
        
        movements = query.order_by(StockMovement.created_at.desc()).all()
        
        data = []
        for m in movements:
            product = db.get(Product, m.product_id)
            data.append({
                'Fecha': m.created_at.strftime('%Y-%m-%d') if m.created_at else '',
                'Hora': m.created_at.strftime('%H:%M:%S') if m.created_at else '',
                'Producto': product.name if product else 'N/A',
                'Código': product.barcode if product else 'N/A',
                'Tipo': 'INGRESO' if m.type == 'IN' else 'VENTA',
                'Cantidad': m.quantity,
                'Importe (USD)': m.quantity * product.sale_price if product else 0,
                'Usuario': m.user_name or 'Sistema'
            })
        
        df = pd.DataFrame(data)
        
        if format == 'csv':
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(filepath, index=False, sheet_name='Movimientos')
        
        return True

    @staticmethod
    def get_default_filename(export_type: str, format: str) -> str:
        """
        Genera un nombre de archivo por defecto con fecha.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = 'csv' if format == 'csv' else 'xlsx'
        
        if export_type == 'inventory':
            return f'inventario_{timestamp}.{extension}'
        else:
            return f'movimientos_{timestamp}.{extension}'
