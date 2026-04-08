"""
InventoryController - Controlador para operaciones de inventario.

Extrae la lógica de negocio de InventoryApp (main.py) para separar
la presentación del control y la lógica de negocio.
"""
from src.database.config import SessionLocal
from src.services.product_service import ProductService
from src.services.stock_service import StockService


class InventoryController:
    """
    Controlador que maneja la lógica de negocio del inventario.
    
    Responsibilities:
    - Control de stock (ingreso/venta)
    - Gestión de productos (activar/desactivar)
    - Lógica de negocio relacionada con inventario
    """
    
    def __init__(self, operator_name: str):
        """
        Inicializa el controlador.
        
        Args:
            operator_name: Nombre del operador actual para auditoría
        """
        self.operator_name = operator_name
    
    def agregar_stock(self, db, product, cantidad: int) -> tuple:
        """
        Registra un ingreso de stock (IN).
        
        Args:
            db: SQLAlchemy session
            product: Producto instance
            cantidad: Cantidad a agregar
            
        Returns:
            tuple: (success: bool, message: str, product)
        """
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0", None
        
        StockService.record_in(db, product.id, cantidad, self.operator_name)
        return True, f"Ingreso: +{cantidad}", product
    
    def descontar_stock(self, db, product, cantidad: int) -> tuple:
        """
        Registra una salida de stock (OUT/Venta).
        
        Args:
            db: SQLAlchemy session
            product: Producto instance
            cantidad: Cantidad a descontar
            
        Returns:
            tuple: (success: bool, message: str, product)
        """
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0", None
        
        # Verificar stock disponible
        if product.stock_qty < cantidad:
            return False, f"Stock insuficiente: {product.stock_qty}", None
        
        StockService.record_out(db, product.id, cantidad, self.operator_name)
        return True, f"Venta: -{cantidad}", product
    
    def modificar_stock(self, db, product, modo: str, cantidad: int) -> tuple:
        """
        Modifica el stock según el modo (IN o OUT).
        
        Args:
            db: SQLAlchemy session
            product: Producto instance
            modo: "IN" para ingreso, "OUT" para venta
            cantidad: Cantidad a modificar
            
        Returns:
            tuple: (success: bool, message: str, product)
        """
        if modo == "OUT" and product.stock_qty < cantidad:
            return False, f"STOCK INSUFICIENTE: {product.name} (disponible: {product.stock_qty})", None
        
        if modo == "IN":
            return self.agregar_stock(db, product, cantidad)
        else:
            return self.descontar_stock(db, product, cantidad)
    
    def activar_producto(self, db, product_id: int) -> tuple:
        """
        Activa (da de alta) un producto.
        
        Args:
            db: SQLAlchemy session
            product_id: ID del producto
            
        Returns:
            tuple: (product, error_message)
        """
        return ProductService.activate(db, product_id)
    
    def desactivar_producto(self, db, product_id: int) -> tuple:
        """
        Desactiva (da de baja) un producto.
        
        Args:
            db: SQLAlchemy session
            product_id: ID del producto
            
        Returns:
            tuple: (product, error_message)
        """
        return ProductService.deactivate(db, product_id)
    
    def obtener_producto_por_barcode(self, db, barcode: str, only_active: bool = True):
        """
        Busca un producto por su código de barras.
        
        Args:
            db: SQLAlchemy session
            barcode: Código de barras
            only_active: Si True, solo retorna productos activos
            
        Returns:
            Product instance o None
        """
        return ProductService.get_by_barcode(db, barcode, only_active=only_active)
    
    def puede_activar(self, producto) -> tuple:
        """
        Verifica si un producto puede ser dado de alta.
        
        Args:
            producto: Producto instance
            
        Returns:
            tuple: (can_activate: bool, reason: str)
        """
        if producto.stock_qty <= 0:
            return False, "Para dar de alta, primero debe registrar un ingreso de stock."
        return True, ""
    
    def puede_desactivar(self, producto) -> tuple:
        """
        Verifica si un producto puede ser dado de baja.
        
        Args:
            producto: Producto instance
            
        Returns:
            tuple: (can_deactivate: bool, reason: str)
        """
        if producto.stock_qty > 0:
            return False, f"Para dar de baja, primero debe vender o retirar todo el stock (actual: {producto.stock_qty})."
        return True, ""
    
    def necesita_alerta_stock(self, producto) -> bool:
        """
        Verifica si el producto está en estado de alerta de stock.
        
        Args:
            producto: Producto instance
            
        Returns:
            bool: True si stock <= min_stock_alert
        """
        return producto.stock_qty <= producto.min_stock_alert
    
    def get_product_movements(self, db, product_id: int):
        """
        Obtiene el historial de movimientos de stock de un producto.
        
        Args:
            db: SQLAlchemy session
            product_id: ID del producto
            
        Returns:
            Lista de StockMovement instances
        """
        return StockService.get_product_movements(db, product_id)
