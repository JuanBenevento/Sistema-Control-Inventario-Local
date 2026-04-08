"""Diálogos para gestionar proveedores."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QLineEdit, QTextEdit, QPushButton,
                              QMessageBox, QListWidget, QListWidgetItem,
                              QWidget, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.database.config import SessionLocal
from src.services.supplier_service import SupplierService


class SupplierDialog(QDialog):
    """Diálogo para crear o editar un proveedor."""

    def __init__(self, supplier=None, parent=None, user_permissions=None):
        """
        Args:
            supplier: Supplier entity para editar, o None para crear nuevo
            parent: Widget padre
            user_permissions: Permisos del usuario actual
        """
        super().__init__(parent)
        self.supplier = supplier
        self.is_new = supplier is None
        self.user_permissions = user_permissions or set()
        self.setWindowTitle("Nuevo Proveedor" if self.is_new else "Editar Proveedor")
        self.setMinimumSize(500, 450)
        self._setup_ui()
        
        if supplier:
            self._populate_form(supplier)

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Datos del Proveedor")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setMaxLength(150)
        self.txt_nombre.setPlaceholderText("Nombre de la empresa...")
        form_layout.addRow("Nombre *:", self.txt_nombre)

        self.txt_contacto = QLineEdit()
        self.txt_contacto.setMaxLength(100)
        self.txt_contacto.setPlaceholderText("Nombre del contacto...")
        form_layout.addRow("Contacto:", self.txt_contacto)

        self.txt_telefono = QLineEdit()
        self.txt_telefono.setMaxLength(30)
        self.txt_telefono.setPlaceholderText("+54 11 1234-5678...")
        form_layout.addRow("Teléfono:", self.txt_telefono)

        self.txt_email = QLineEdit()
        self.txt_email.setMaxLength(100)
        self.txt_email.setPlaceholderText("email@ejemplo.com...")
        form_layout.addRow("Email:", self.txt_email)

        self.txt_direccion = QLineEdit()
        self.txt_direccion.setMaxLength(255)
        self.txt_direccion.setPlaceholderText("Dirección completa...")
        form_layout.addRow("Dirección:", self.txt_direccion)

        self.txt_notas = QTextEdit()
        self.txt_notas.setMaximumHeight(60)
        self.txt_notas.setPlaceholderText("Notas adicionales...")
        form_layout.addRow("Notas:", self.txt_notas)

        layout.addLayout(form_layout)

        layout.addStretch()

        nota = QLabel("* Campos requeridos")
        nota.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(nota)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(100, 35)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setFixedSize(100, 35)
        btn_guardar.setDefault(True)
        btn_guardar.clicked.connect(self._on_guardar)
        btn_layout.addWidget(btn_guardar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _populate_form(self, supplier):
        """Llena el formulario con datos del proveedor."""
        self.txt_nombre.setText(supplier.name)
        self.txt_contacto.setText(supplier.contact_name or "")
        self.txt_telefono.setText(supplier.phone or "")
        self.txt_email.setText(supplier.email or "")
        self.txt_direccion.setText(supplier.address or "")
        self.txt_notas.setPlainText(supplier.notes or "")

    def _on_guardar(self):
        """Valida y acepta el diálogo."""
        name = self.txt_nombre.text().strip()
        if not name:
            self.txt_nombre.setFocus()
            return
        
        self.accept()

    def get_data(self):
        """Retorna los datos del formulario."""
        return {
            "name": self.txt_nombre.text().strip(),
            "contact_name": self.txt_contacto.text().strip() or None,
            "phone": self.txt_telefono.text().strip() or None,
            "email": self.txt_email.text().strip() or None,
            "address": self.txt_direccion.text().strip() or None,
            "notes": self.txt_notas.toPlainText().strip() or None,
        }


class SupplierManagerDialog(QDialog):
    """Diálogo para gestionar proveedores (lista con CRUD)."""

    def __init__(self, parent=None, user_permissions=None):
        super().__init__(parent)
        self.user_permissions = user_permissions or set()
        self.setWindowTitle("Gestionar Proveedores")
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Proveedores")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        self.lista = QListWidget()
        self.lista.itemDoubleClicked.connect(self._on_edit)
        layout.addWidget(self.lista)

        btn_layout = QHBoxLayout()
        
        btn_nuevo = QPushButton("Nuevo")
        btn_nuevo.clicked.connect(self._on_new)
        btn_layout.addWidget(btn_nuevo)
        
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self._on_edit)
        btn_layout.addWidget(btn_editar)
        
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self._on_delete)
        btn_layout.addWidget(btn_eliminar)
        
        btn_layout.addStretch()
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_suppliers(self):
        """Carga los proveedores en la lista."""
        self.lista.clear()
        db = SessionLocal()
        try:
            service = SupplierService(self.user_permissions)
            suppliers = service.get_all(db)
            
            for s in suppliers:
                display = f"{s.name}"
                if s.contact_name:
                    display += f" - {s.contact_name}"
                if s.phone:
                    display += f" | {s.phone}"
                
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, s.id)
                self.lista.addItem(item)
        finally:
            db.close()

    def _on_new(self):
        """Crea un nuevo proveedor."""
        dialog = SupplierDialog(parent=self, user_permissions=self.user_permissions)
        if dialog.exec():
            data = dialog.get_data()
            db = SessionLocal()
            try:
                service = SupplierService(self.user_permissions)
                result, error = service.create(db, **data)
                if error:
                    QMessageBox.warning(self, "Error", error)
                else:
                    self._load_suppliers()
            finally:
                db.close()

    def _on_edit(self):
        """Edita el proveedor seleccionado."""
        item = self.lista.currentItem()
        if not item:
            return
        
        supplier_id = item.data(Qt.UserRole)
        db = SessionLocal()
        try:
            from src.repository.supplier_repository import SupplierRepository
            supplier = SupplierRepository.get_by_id(db, supplier_id)
            if not supplier:
                return
            
            dialog = SupplierDialog(
                supplier=supplier,
                parent=self,
                user_permissions=self.user_permissions
            )
            if dialog.exec():
                data = dialog.get_data()
                service = SupplierService(self.user_permissions)
                result, error = service.update(db, supplier_id, **data)
                if error:
                    QMessageBox.warning(self, "Error", error)
                else:
                    self._load_suppliers()
        finally:
            db.close()
    
    def _on_delete(self):
        """Elimina el proveedor seleccionado."""
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, "Atención", "Seleccione un proveedor para eliminar.")
            return
        
        supplier_id = item.data(Qt.UserRole)
        
        confirmar = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar este proveedor?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmar == QMessageBox.Yes:
            db = SessionLocal()
            try:
                service = SupplierService(self.user_permissions)
                success, error = service.delete(db, supplier_id)
                if error:
                    QMessageBox.warning(self, "Error", error)
                else:
                    self._load_suppliers()
                    QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente.")
            finally:
                db.close()