"""Diálogo para crear/editar categorías."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
                              QMessageBox, QListWidget, QListWidgetItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.database.config import SessionLocal
from src.services.category_service import CategoryService


class CategoryDialog(QDialog):
    """Diálogo para crear o editar una categoría."""

    def __init__(self, category=None, parent=None, user_permissions=None):
        super().__init__(parent)
        self.category = category
        self.is_new = category is None
        self.user_permissions = user_permissions or set()
        self.setWindowTitle("Nueva Categoría" if self.is_new else "Editar Categoría")
        self.setMinimumSize(450, 350)
        self._setup_ui()
        
        if category:
            self._populate_form(category)

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Datos de Categoría")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setMaxLength(100)
        self.txt_nombre.setPlaceholderText("Nombre de la categoría...")
        form_layout.addRow("Nombre *:", self.txt_nombre)

        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setMaximumHeight(80)
        self.txt_descripcion.setPlaceholderText("Descripción (opcional)...")
        form_layout.addRow("Descripción:", self.txt_descripcion)

        self.cmb_padre = QComboBox()
        self.cmb_padre.addItem("-- Sin categoría padre --", None)
        self._load_parent_categories()
        form_layout.addRow("Categoría padre:", self.cmb_padre)

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

    def _load_parent_categories(self):
        db = SessionLocal()
        try:
            service = CategoryService(self.user_permissions)
            roots = service.get_root_categories(db)
            for cat in roots:
                if self.category and cat.id == self.category.id:
                    continue
                self.cmb_padre.addItem(cat.name, cat.id)
        finally:
            db.close()

    def _populate_form(self, category):
        self.txt_nombre.setText(category.name)
        self.txt_descripcion.setText(category.description or "")
        
        if category.parent_id:
            index = self.cmb_padre.findData(category.parent_id)
            if index >= 0:
                self.cmb_padre.setCurrentIndex(index)

    def _on_guardar(self):
        name = self.txt_nombre.text().strip()
        if not name:
            self.txt_nombre.setFocus()
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.txt_nombre.text().strip(),
            "description": self.txt_descripcion.toPlainText().strip() or None,
            "parent_id": self.cmb_padre.currentData(),
        }


class CategoryManagerDialog(QDialog):
    """Diálogo para gestionar categorías."""

    def __init__(self, parent=None, user_permissions=None):
        super().__init__(parent)
        self.user_permissions = user_permissions or set()
        self.setWindowTitle("Gestionar Categorías")
        self.setMinimumSize(600, 500)
        self._setup_ui()
        self._load_categories()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Categorías")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        self.lista = QListWidget()
        self.lista.itemDoubleClicked.connect(self._on_edit)
        layout.addWidget(self.lista)

        btn_layout = QHBoxLayout()
        
        btn_nuevo = QPushButton("Nueva")
        btn_nuevo.clicked.connect(self._on_new)
        btn_layout.addWidget(btn_nuevo)
        
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self._on_edit)
        btn_layout.addWidget(btn_editar)
        
        btn_layout.addStretch()
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_categories(self):
        self.lista.clear()
        db = SessionLocal()
        try:
            service = CategoryService(self.user_permissions)
            categories = service.get_all_with_hierarchy(db)
            
            for cat, level, display_name in categories:
                item = QListWidgetItem(display_name)
                item.setData(Qt.UserRole, cat.id)
                self.lista.addItem(item)
        finally:
            db.close()

    def _on_new(self):
        dialog = CategoryDialog(parent=self, user_permissions=self.user_permissions)
        if dialog.exec():
            data = dialog.get_data()
            db = SessionLocal()
            try:
                service = CategoryService(self.user_permissions)
                result, error = service.create(db, **data)
                if error:
                    QMessageBox.warning(self, "Error", error)
                else:
                    self._load_categories()
            finally:
                db.close()

    def _on_edit(self):
        item = self.lista.currentItem()
        if not item:
            return
        
        category_id = item.data(Qt.UserRole)
        db = SessionLocal()
        try:
            from src.repository.category_repository import CategoryRepository
            category = CategoryRepository.get_by_id(db, category_id)
            if not category:
                return
            
            dialog = CategoryDialog(
                category=category,
                parent=self,
                user_permissions=self.user_permissions
            )
            if dialog.exec():
                data = dialog.get_data()
                service = CategoryService(self.user_permissions)
                result, error = service.update(db, category_id, **data)
                if error:
                    QMessageBox.warning(self, "Error", error)
                else:
                    self._load_categories()
        finally:
            db.close()