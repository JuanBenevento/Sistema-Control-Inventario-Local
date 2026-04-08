from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QFormLayout, QLabel, QLineEdit, 
                              QDoubleSpinBox, QSpinBox, QPushButton, QSizePolicy, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.database.config import SessionLocal


class ProductEditDialog(QDialog):
    """Dialogo para editar/crear productos."""
    
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.is_new = product is None or not getattr(product, 'id', None)
        self.setMinimumWidth(400)
        
        # Configurar UI una sola vez
        self._setup_ui()
        self._connect_signals()
        
        # Configurar según modo (nuevo/editar)
        if self.is_new:
            self.setWindowTitle("Nuevo Producto")
            # Si viene con barcode predefinido (desde escaneo)
            if product and getattr(product, 'barcode', None):
                self.txt_barcode.setText(product.barcode)
        else:
            self.setWindowTitle("Editar Producto")
            self._populate_form(product)
    
    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Datos del Producto")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        main_layout.addWidget(title)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(12)
        
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("Código:"))
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setMaxLength(50)
        self.txt_barcode.setPlaceholderText("Código de barras...")
        self.txt_barcode.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        code_layout.addWidget(self.txt_barcode)
        text_layout.addLayout(code_layout)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nombre:"))
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setMaxLength(100)
        self.txt_nombre.setPlaceholderText("Nombre del producto...")
        self.txt_nombre.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        name_layout.addWidget(self.txt_nombre)
        text_layout.addLayout(name_layout)
        
        brand_layout = QHBoxLayout()
        brand_layout.addWidget(QLabel("Marca:"))
        self.txt_marca = QLineEdit()
        self.txt_marca.setMaxLength(100)
        self.txt_marca.setPlaceholderText("Marca (opcional)...")
        self.txt_marca.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        brand_layout.addWidget(self.txt_marca)
        text_layout.addLayout(brand_layout)
        
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Categoría:"))
        self.cmb_categoria = QComboBox()
        self.cmb_categoria.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cmb_categoria.setFixedHeight(36)
        self._load_categories()
        category_layout.addWidget(self.cmb_categoria)
        text_layout.addLayout(category_layout)
        
        supplier_layout = QHBoxLayout()
        supplier_layout.addWidget(QLabel("Proveedor:"))
        self.cmb_proveedor = QComboBox()
        self.cmb_proveedor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cmb_proveedor.setFixedHeight(36)
        self._load_suppliers()
        supplier_layout.addWidget(self.cmb_proveedor)
        text_layout.addLayout(supplier_layout)
        
        main_layout.addLayout(text_layout)
        
        price_layout = QGridLayout()
        price_layout.setSpacing(12)
        
        lbl_costo = QLabel("Costo (USD):")
        lbl_costo.setFont(QFont("Segoe UI", 10))
        self.spn_costo = QDoubleSpinBox()
        self.spn_costo.setRange(0, 999999.99)
        self.spn_costo.setDecimals(2)
        self.spn_costo.setPrefix("$ ")
        self.spn_costo.setFixedHeight(36)
        self.spn_costo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        lbl_margen = QLabel("Margen (%):")
        lbl_margen.setFont(QFont("Segoe UI", 10))
        self.spn_margen = QDoubleSpinBox()
        self.spn_margen.setRange(0, 500)
        self.spn_margen.setDecimals(1)
        self.spn_margen.setValue(30.0)
        self.spn_margen.setSuffix(" %")
        self.spn_margen.setFixedHeight(36)
        self.spn_margen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        price_layout.addWidget(lbl_costo, 0, 0)
        price_layout.addWidget(self.spn_costo, 0, 1)
        price_layout.addWidget(lbl_margen, 0, 2)
        price_layout.addWidget(self.spn_margen, 0, 3)
        
        lbl_venta = QLabel("Precio Venta (USD):")
        lbl_venta.setFont(QFont("Segoe UI", 10))
        self.spn_venta = QDoubleSpinBox()
        self.spn_venta.setRange(0, 999999.99)
        self.spn_venta.setDecimals(2)
        self.spn_venta.setPrefix("$ ")
        self.spn_venta.setFixedHeight(36)
        self.spn_venta.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        lbl_min_stock = QLabel("Stock Mínimo:")
        lbl_min_stock.setFont(QFont("Segoe UI", 10))
        self.spn_min_stock = QSpinBox()
        self.spn_min_stock.setRange(0, 9999)
        self.spn_min_stock.setValue(2)
        self.spn_min_stock.setFixedHeight(36)
        self.spn_min_stock.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        price_layout.addWidget(lbl_venta, 1, 0)
        price_layout.addWidget(self.spn_venta, 1, 1)
        price_layout.addWidget(lbl_min_stock, 1, 2)
        price_layout.addWidget(self.spn_min_stock, 1, 3)
        
        price_layout.setColumnStretch(1, 1)
        price_layout.setColumnStretch(3, 1)
        
        main_layout.addLayout(price_layout)
        
        main_layout.addStretch()
        
        nota = QLabel("* Campos requeridos")
        nota.setStyleSheet("color: #888; font-size: 10px;")
        nota.setAlignment(Qt.AlignRight)
        main_layout.addWidget(nota)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(120, 40)
        btn_cancelar.setFont(QFont("Segoe UI", 10))
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedSize(120, 40)
        btn_guardar.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_guardar.setDefault(True)
        btn_guardar.clicked.connect(self._on_guardar)
        btn_layout.addWidget(btn_guardar)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.setMinimumSize(450, 420)
    
    def _connect_signals(self):
        self.spn_costo.valueChanged.connect(self._on_costo_or_margen_changed)
        self.spn_margen.valueChanged.connect(self._on_costo_or_margen_changed)
    
    def _on_costo_or_margen_changed(self):
        self.spn_venta.setValue(self._calcular_precio_venta())
    
    def _calcular_precio_venta(self):
        costo = self.spn_costo.value()
        margen = self.spn_margen.value()
        return costo * (1 + margen / 100)
    
    def _load_categories(self):
        db = SessionLocal()
        try:
            from src.services.category_service import CategoryService
            service = CategoryService()
            categories = service.get_all(db)
            self.cmb_categoria.clear()
            self.cmb_categoria.addItem("-- Sin categoría --", None)
            for cat in categories:
                self.cmb_categoria.addItem(cat.name, cat.id)
        finally:
            db.close()
    
    def _load_suppliers(self):
        db = SessionLocal()
        try:
            from src.services.supplier_service import SupplierService
            service = SupplierService()
            suppliers = service.get_all(db)
            self.cmb_proveedor.clear()
            self.cmb_proveedor.addItem("-- Sin proveedor --", None)
            for s in suppliers:
                self.cmb_proveedor.addItem(s.name, s.id)
        finally:
            db.close()
    
    def _populate_form(self, product):
        """Llena el formulario con datos del producto."""
        self.txt_barcode.setText(product.barcode)
        self.txt_barcode.setReadOnly(True)
        self.txt_nombre.setText(product.name)
        self.txt_marca.setText(product.brand or "")
        self.spn_costo.setValue(product.cost_usd)
        
        if product.sale_price and product.sale_price > 0 and product.cost_usd:
            margen = ((product.sale_price - product.cost_usd) / product.sale_price) * 100
            self.spn_margen.setValue(margen)
        else:
            self.spn_margen.setValue(30.0)
        
        self.spn_venta.setValue(product.sale_price)
        self.spn_min_stock.setValue(product.min_stock_alert)
        
        if product.category_id:
            index = self.cmb_categoria.findData(product.category_id)
            if index >= 0:
                self.cmb_categoria.setCurrentIndex(index)
        
        if product.supplier_id:
            index = self.cmb_proveedor.findData(product.supplier_id)
            if index >= 0:
                self.cmb_proveedor.setCurrentIndex(index)
    
    def _on_guardar(self):
        """Valida y acepta el diálogo."""
        if not self.txt_barcode.text().strip():
            self.txt_barcode.setFocus()
            self.txt_barcode.selectAll()
            return
        if not self.txt_nombre.text().strip():
            self.txt_nombre.setFocus()
            self.txt_nombre.selectAll()
            return
        self.accept()
    
    def get_data(self):
        """Retorna los datos del formulario."""
        return {
            "barcode": self.txt_barcode.text().strip(),
            "name": self.txt_nombre.text().strip(),
            "brand": self.txt_marca.text().strip(),
            "cost_usd": self.spn_costo.value(),
            "sale_price": self.spn_venta.value(),
            "min_stock_alert": self.spn_min_stock.value(),
            "category_id": self.cmb_categoria.currentData(),
            "supplier_id": self.cmb_proveedor.currentData(),
        }
