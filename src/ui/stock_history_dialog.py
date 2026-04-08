from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                              QTableView, QLabel, QPushButton, QHeaderView, QWidget)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont, QColor


class StockMovementModel(QAbstractTableModel):
    """Table model for displaying stock movement history."""
    
    HEADERS = ["Fecha", "Hora", "Usuario", "Tipo", "Cantidad"]
    
    def __init__(self, movements=None):
        super().__init__()
        self._movements = movements or []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._movements)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        movement = self._movements[index.row()]
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                # Fecha
                if movement.created_at:
                    return movement.created_at.strftime("%d/%m/%Y")
                return ""
            elif index.column() == 1:
                # Hora
                if movement.created_at:
                    return movement.created_at.strftime("%H:%M:%S")
                return ""
            elif index.column() == 2:
                return movement.user_name or "Sistema"
            elif index.column() == 3:
                return "INGRESO" if movement.type == "IN" else "VENTA"
            elif index.column() == 4:
                return str(movement.quantity)
        
        # Color coding: green for IN, red for OUT
        if role == Qt.ForegroundRole and index.column() == 3:
            if movement.type == "IN":
                return QColor("#27ae60")  # Verde
            elif movement.type == "OUT":
                return QColor("#e74c3c")  # Rojo
        
        # Centrar texto en columnas
        if role == Qt.TextAlignmentRole:
            if index.column() in [0, 1, 4]:
                return Qt.AlignCenter
            return Qt.AlignLeft
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None
    
    def update_movements(self, movements):
        self.beginResetModel()
        self._movements = movements
        self.endResetModel()


class StockHistoryDialog(QDialog):
    """Dialog to display stock movement history for a product."""
    
    def __init__(self, product, db_session, parent=None):
        super().__init__(parent)
        self.product = product
        self.db_session = db_session
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_movements()
    
    def _setup_ui(self):
        self.setWindowTitle(f"Historial - {self.product.name}")
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header con info del producto
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel(f"<h2>📦 {self.product.name}</h2>")
        name_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        info_label = QLabel(
            f"<span style='color: #555;'>Marca:</span> {self.product.brand or 'N/A'} &nbsp;&nbsp; "
            f"<span style='color: #555;'>Código:</span> {self.product.barcode} &nbsp;&nbsp; "
            f"<span style='color: #555;'>Stock Actual:</span> <b>{self.product.stock_qty}</b>"
        )
        info_label.setFont(QFont("Segoe UI", 10))
        
        header_layout.addWidget(name_label)
        header_layout.addWidget(info_label)
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)
        
        # Separador
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #ddd;")
        main_layout.addWidget(separator)
        
        # Tabla de movimientos
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setFont(QFont("Segoe UI", 10))
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.verticalHeader().setVisible(False)
        
        # Auto-resize columns
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        main_layout.addWidget(self.table_view)
        
        # Contador de movimientos
        self.counter_label = QLabel()
        self.counter_label.setFont(QFont("Segoe UI", 9))
        self.counter_label.setStyleSheet("color: #888;")
        main_layout.addWidget(self.counter_label)
        
        # Botón cerrar
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Cerrar")
        close_btn.setFixedSize(120, 35)
        close_btn.setFont(QFont("Segoe UI", 10))
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        main_layout.addLayout(close_layout)
        
        self.setLayout(main_layout)
    
    def _load_movements(self):
        from src.repository.stock_movement_repository import StockMovementRepository
        
        movements = StockMovementRepository.get_by_product(self.db_session, self.product.id)
        
        model = StockMovementModel(movements)
        self.table_view.setModel(model)
        
        # Actualizar contador
        total_in = sum(m.quantity for m in movements if m.type == "IN")
        total_out = sum(m.quantity for m in movements if m.type == "OUT")
        
        self.counter_label.setText(
            f"Total movimientos: {len(movements)} | "
            f"📥 Ingresos: {total_in} | "
            f"📤 Ventas: {total_out}"
        )
        
        # Resize columns proportionally
        self.table_view.resizeColumnsToContents()
