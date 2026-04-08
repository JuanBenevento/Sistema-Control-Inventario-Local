"""
Diálogo para exportar datos.
"""
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QPushButton, QWidget, QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from src.services.export_service import ExportService
from src.database.config import SessionLocal


class ExportDialog(QDialog):
    """Diálogo para seleccionar opciones de exportación."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.export_service = ExportService()
        self.setWindowTitle("Exportar Datos")
        self.setMinimumSize(400, 300)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📥 Exportar Datos")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        tipo_layout = QHBoxLayout()
        tipo_label = QLabel("Tipo de exportación:")
        tipo_label.setFont(QFont("Segoe UI", 10))
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Inventario completo", "Historial de movimientos"])
        self.cmb_tipo.setFont(QFont("Segoe UI", 10))
        self.cmb_tipo.setFixedHeight(35)
        tipo_layout.addWidget(tipo_label)
        tipo_layout.addWidget(self.cmb_tipo)
        layout.addLayout(tipo_layout)

        formato_layout = QHBoxLayout()
        formato_label = QLabel("Formato:")
        formato_label.setFont(QFont("Segoe UI", 10))
        self.cmb_formato = QComboBox()
        self.cmb_formato.addItems(["CSV (hoja de cálculo)", "Excel (.xlsx)"])
        self.cmb_formato.setFont(QFont("Segoe UI", 10))
        self.cmb_formato.setFixedHeight(35)
        formato_layout.addWidget(formato_label)
        formato_layout.addWidget(self.cmb_formato)
        layout.addLayout(formato_layout)

        self.fecha_widget = QWidget()
        fecha_layout = QVBoxLayout()
        fecha_layout.setContentsMargins(0, 10, 0, 0)
        
        fecha_title = QLabel("Rango de fechas (opcional):")
        fecha_title.setFont(QFont("Segoe UI", 10))
        fecha_layout.addWidget(fecha_title)
        
        fecha_inner = QHBoxLayout()
        
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addMonths(-1))
        self.date_start.setFont(QFont("Segoe UI", 10))
        self.date_start.setFixedHeight(35)
        fecha_inner.addWidget(QLabel("Desde:"))
        fecha_inner.addWidget(self.date_start)
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setFont(QFont("Segoe UI", 10))
        self.date_end.setFixedHeight(35)
        fecha_inner.addWidget(QLabel("Hasta:"))
        fecha_inner.addWidget(self.date_end)
        
        fecha_layout.addLayout(fecha_inner)
        self.fecha_widget.setLayout(fecha_layout)
        self.fecha_widget.setVisible(False)
        
        self.cmb_tipo.currentIndexChanged.connect(self._on_tipo_changed)
        
        layout.addWidget(self.fecha_widget)

        layout.addStretch()

        self.lbl_status = QLabel()
        self.lbl_status.setFont(QFont("Segoe UI", 9))
        self.lbl_status.setStyleSheet("color: #888;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(100, 40)
        btn_cancelar.setFont(QFont("Segoe UI", 10))
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_exportar = QPushButton("Exportar")
        btn_exportar.setFixedSize(100, 40)
        btn_exportar.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_exportar.setStyleSheet("""
            QPushButton { background: #27ae60; color: white; border: none; border-radius: 5px; }
            QPushButton:hover { background: #219a52; }
        """)
        btn_exportar.clicked.connect(self._on_exportar)
        btn_layout.addWidget(btn_exportar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _on_tipo_changed(self, index):
        self.fecha_widget.setVisible(index == 1)

    def _on_exportar(self):
        from PySide6.QtWidgets import QFileDialog

        tipo = self.cmb_tipo.currentIndex()
        formato_index = self.cmb_formato.currentIndex()
        formato = 'csv' if formato_index == 0 else 'excel'
        
        if formato == 'csv':
            extension = 'csv'
            filter_str = "CSV (*.csv)"
        else:
            extension = 'xlsx'
            filter_str = "Excel (*.xlsx)"
        
        export_type = 'inventory' if tipo == 0 else 'movements'
        default_name = self.export_service.get_default_filename(export_type, formato)
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo",
            default_name,
            filter_str
        )
        
        if not filename:
            return
        
        if not filename.endswith(f'.{extension}'):
            filename = f'{filename}.{extension}'
        
        self.lbl_status.setText("Exportando...")
        self.lbl_status.setStyleSheet("color: #3498db;")
        
        try:
            db = SessionLocal()
            
            if tipo == 0:
                self.export_service.export_inventory(db, filename, formato)
            else:
                start_date = self.date_start.date().toPython()
                end_date = self.date_end.date().toPython().replace(hour=23, minute=59, second=59)
                
                self.export_service.export_movements(
                    db, filename, formato,
                    start_date=start_date,
                    end_date=end_date
                )
            
            db.close()
            
            self.lbl_status.setText(f"✅ Exportado: {filename}")
            self.lbl_status.setStyleSheet("color: #27ae60;")
            
        except Exception as e:
            self.lbl_status.setText(f"❌ Error: {str(e)}")
            self.lbl_status.setStyleSheet("color: #e74c3c;")
