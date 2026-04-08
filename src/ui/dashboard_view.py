"""
Vista del Dashboard con KPIs.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.services.dashboard_service import DashboardService


class DashboardView(QWidget):
    """Widget del Dashboard con métricas clave."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_service = DashboardService()
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Título
        title = QLabel("📊 Dashboard")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        main_layout.addWidget(title)

        # Cards de ventas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Card ventas del día
        self.card_hoy = self._create_sales_card("HOY", "#3498db")
        cards_layout.addWidget(self.card_hoy)

        # Card ventas semana
        self.card_semana = self._create_sales_card("ESTA SEMANA", "#2ecc71")
        cards_layout.addWidget(self.card_semana)

        # Card ventas mes
        self.card_mes = self._create_sales_card("ESTE MES", "#9b59b6")
        cards_layout.addWidget(self.card_mes)

        main_layout.addLayout(cards_layout)

        # Sección inferior
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        # Stock bajo
        stock_widget = self._create_section_widget("⚠️ STOCK BAJO")
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(3)
        self.stock_table.setHorizontalHeaderLabels(["Producto", "Stock", "Mínimo"])
        self.stock_table.setMaximumHeight(150)
        stock_widget.layout().addWidget(self.stock_table)
        bottom_layout.addWidget(stock_widget, 1)

        # Top productos
        top_widget = self._create_section_widget("🏆 TOP PRODUCTOS")
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(2)
        self.top_table.setHorizontalHeaderLabels(["Producto", "Vendidos"])
        self.top_table.setMaximumHeight(150)
        top_widget.layout().addWidget(self.top_table)
        bottom_layout.addWidget(top_widget, 1)

        main_layout.addLayout(bottom_layout)

        # Resumen margen
        self.margin_label = QLabel()
        self.margin_label.setFont(QFont("Segoe UI", 12))
        self.margin_label.setStyleSheet("color: #27ae60; padding: 10px; background: #e8f8f5; border-radius: 5px;")
        self.margin_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.margin_label)

        # Botón actualizar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.setFixedSize(120, 35)
        btn_refresh.clicked.connect(self.refresh_data)
        btn_layout.addWidget(btn_refresh)
        
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def _create_sales_card(self, title: str, color: str) -> QWidget:
        """Crea una card de métricas de ventas."""
        card = QWidget()
        card.setMinimumHeight(100)
        card.setStyleSheet(f"""
            QWidget {{
                background: {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: rgba(255,255,255,180);")
        layout.addWidget(title_label)
        
        self._sales_labels = getattr(self, '_sales_labels', {})
        self._sales_labels[title] = {}
        
        amount = QLabel("$ 0.00")
        amount.setFont(QFont("Segoe UI", 20, QFont.Bold))
        amount.setStyleSheet("color: white;")
        self._sales_labels[title]['amount'] = amount
        layout.addWidget(amount)
        
        count = QLabel("0 ventas")
        count.setFont(QFont("Segoe UI", 9))
        count.setStyleSheet("color: rgba(255,255,255,200);")
        self._sales_labels[title]['count'] = count
        layout.addWidget(count)
        
        card.setLayout(layout)
        return card

    def _create_section_widget(self, title: str) -> QWidget:
        """Crea un widget de sección con título."""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)
        
        widget.setLayout(layout)
        return widget

    def refresh_data(self):
        """Actualiza todos los datos del dashboard."""
        # Ventas del día
        daily = self.dashboard_service.get_daily_sales()
        self._update_sales_card("HOY", daily)
        
        # Ventas semana
        weekly = self.dashboard_service.get_weekly_sales()
        self._update_sales_card("ESTA SEMANA", weekly)
        
        # Ventas mes
        monthly = self.dashboard_service.get_monthly_sales()
        self._update_sales_card("ESTE MES", monthly)
        
        # Stock bajo
        low_stock = self.dashboard_service.get_low_stock_alerts()
        self._update_stock_table(low_stock)
        
        # Top productos
        top_products = self.dashboard_service.get_top_selling_products()
        self._update_top_table(top_products)
        
        # Margen
        margin = self.dashboard_service.get_margin_summary()
        self.margin_label.setText(f"💰 MARGEN PROMEDIO: {margin['average']:.1f}% ({margin['count']} productos con precio)")

    def _update_sales_card(self, key: str, data: dict):
        if hasattr(self, '_sales_labels') and key in self._sales_labels:
            self._sales_labels[key]['amount'].setText(f"$ {data['total']:.2f}")
            self._sales_labels[key]['count'].setText(f"{data['count']} ventas")

    def _update_stock_table(self, products: list):
        self.stock_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.stock_table.setItem(row, 0, QTableWidgetItem(p.name))
            self.stock_table.setItem(row, 1, QTableWidgetItem(str(p.stock_qty)))
            self.stock_table.setItem(row, 2, QTableWidgetItem(str(p.min_stock_alert)))
        
        # Resaltar stock muy bajo en rojo
        for row in range(len(products)):
            if products[row].stock_qty == 0:
                for col in range(3):
                    item = self.stock_table.item(row, col)
                    if item:
                        item.setBackground(Qt.red)
                        item.setForeground(Qt.white)

    def _update_top_table(self, products: list):
        self.top_table.setRowCount(len(products))
        for row, (product, quantity) in enumerate(products):
            self.top_table.setItem(row, 0, QTableWidgetItem(product.name))
            self.top_table.setItem(row, 1, QTableWidgetItem(str(quantity)))