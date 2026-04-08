from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor


class InventoryTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ["Código", "Nombre", "Marca", "Stock", "Costo", "Margen %", "Venta"]
        self._sort_column = 1  # Default sort by Nombre
        self._sort_order = Qt.AscendingOrder

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        product = self._data[index.row()]
        is_inactive = not getattr(product, 'is_active', True)
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                text = product.barcode
            elif index.column() == 1:
                text = product.name
            elif index.column() == 2:
                text = product.brand or "-"
            elif index.column() == 3:
                text = str(product.stock_qty)
            elif index.column() == 4:
                text = f"$ {product.cost_usd:.2f}"
            elif index.column() == 5:
                margin = product.margin_percentage
                text = f"{margin:.1f}%"
            elif index.column() == 6:
                text = f"$ {product.sale_price:.2f}"
            else:
                return None
            
            # Si está inactivo, agregar estilo
            if is_inactive:
                text = text  # Mostrar normal, el color indica el estado
            
            return text
        
        # Color de texto para productos inactivos
        if role == Qt.ForegroundRole:
            if is_inactive:
                return QColor("#999999")  # Gris
        
        # Fondo gris para filas inactivas
        if role == Qt.BackgroundRole and is_inactive:
            return QColor("#f5f5f5")
        
        # Resaltar stock bajo en rojo usando min_stock_alert configurado
        if role == Qt.ForegroundRole and index.column() == 3:
            if product.stock_qty <= product.min_stock_alert:
                return QColor("#e74c3c")
        
        # Fondo rojo claro para stock bajo
        if role == Qt.BackgroundRole and index.column() == 3:
            if product.stock_qty <= product.min_stock_alert:
                return QColor("#ffe6e6")
        
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def update_data(self, new_data):
        self.beginResetModel()
        self._data = self._sort_data(new_data)
        self.endResetModel()

    def _sort_data(self, data):
        """Sort data by the current sort column and order."""
        reverse = self._sort_order == Qt.DescendingOrder
        if self._sort_column == 0:
            return sorted(data, key=lambda p: p.barcode, reverse=reverse)
        elif self._sort_column == 1:
            return sorted(data, key=lambda p: p.name or "", reverse=reverse)
        elif self._sort_column == 2:
            return sorted(data, key=lambda p: p.brand or "", reverse=reverse)
        elif self._sort_column == 3:
            return sorted(data, key=lambda p: p.stock_qty, reverse=reverse)
        elif self._sort_column == 4:
            return sorted(data, key=lambda p: p.cost_usd, reverse=reverse)
        elif self._sort_column == 5:
            return sorted(data, key=lambda p: p.margin_percentage, reverse=reverse)
        elif self._sort_column == 6:
            return sorted(data, key=lambda p: p.sale_price, reverse=reverse)
        return data

    def sort(self, column, order=Qt.AscendingOrder):
        """Sort the model by the given column and order."""
        self._sort_column = column
        self._sort_order = order
        self.beginResetModel()
        self._data = self._sort_data(self._data)
        self.endResetModel()

    def set_sort(self, column, order):
        """Public method to set sort column and order."""
        self.sort(column, order)
