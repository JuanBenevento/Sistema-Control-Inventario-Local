"""Diálogos para gestionar usuarios."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QLineEdit, QPushButton, QMessageBox,
                              QListWidget, QListWidgetItem, QComboBox, QCheckBox,
                              QWidget, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.database.config import SessionLocal
from src.models.entities import User
from src.models.permissions import ROLES
from src.repository.user_repository import UserRepository
from src.utils.auth import hash_password
from src.services.user_service import UserService


class UserDialog(QDialog):
    """Diálogo para crear o editar un usuario."""

    def __init__(self, user=None, parent=None, is_new=False):
        super().__init__(parent)
        self.user = user
        self.is_new = is_new or user is None
        self.setWindowTitle("Nuevo Usuario" if self.is_new else "Editar Usuario")
        self.setMinimumSize(400, 400)
        self._setup_ui()
        
        if user:
            self._populate_form(user)

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Datos del Usuario")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setMaxLength(50)
        self.txt_usuario.setPlaceholderText("Nombre de usuario...")
        if not self.is_new:
            self.txt_usuario.setReadOnly(True)
        form_layout.addRow("Usuario *:", self.txt_usuario)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setMaxLength(100)
        self.txt_nombre.setPlaceholderText("Nombre completo...")
        form_layout.addRow("Nombre:", self.txt_nombre)

        self.txt_password = QLineEdit()
        self.txt_password.setMaxLength(50)
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Contraseña..." if self.is_new else "Nueva contraseña (dejar vacío para no cambiar)...")
        form_layout.addRow("Contraseña:", self.txt_password)

        self.cmb_rol = QComboBox()
        self.cmb_rol.addItems(["vendedor", "admin"])
        form_layout.addRow("Rol:", self.cmb_rol)

        self.chk_activo = QCheckBox("Usuario activo")
        self.chk_activo.setChecked(True)
        form_layout.addRow("", self.chk_activo)

        layout.addLayout(form_layout)

        layout.addStretch()

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

    def _populate_form(self, user):
        """Llena el formulario con datos del usuario."""
        self.txt_usuario.setText(user.username)
        self.txt_nombre.setText(user.full_name or "")
        
        role = getattr(user, 'role', 'vendedor')
        index = self.cmb_rol.findText(role)
        if index >= 0:
            self.cmb_rol.setCurrentIndex(index)
        
        self.chk_activo.setChecked(user.is_active)

    def _on_guardar(self):
        """Valida y acepta el diálogo."""
        username = self.txt_usuario.text().strip()
        if not username:
            self.txt_usuario.setFocus()
            return
        
        if self.is_new and not self.txt_password.text():
            self.txt_password.setFocus()
            return
        
        self.accept()

    def get_data(self):
        """Retorna los datos del formulario."""
        return {
            "username": self.txt_usuario.text().strip(),
            "full_name": self.txt_nombre.text().strip() or None,
            "password": self.txt_password.text() if self.txt_password.text() else None,
            "role": self.cmb_rol.currentText(),
            "is_active": self.chk_activo.isChecked(),
        }


class UserManagerDialog(QDialog):
    """Diálogo para gestionar usuarios."""

    def __init__(self, parent=None, user_permissions=None, current_user=None):
        super().__init__(parent)
        self.user_permissions = user_permissions or set()
        self.current_user = current_user
        self.setWindowTitle("Gestionar Usuarios")
        self.setMinimumSize(600, 450)
        self._setup_ui()
        self._load_users()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Usuarios del Sistema")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        self.lista = QListWidget()
        self.lista.itemDoubleClicked.connect(self._on_edit)
        layout.addWidget(self.lista)

        btn_layout = QHBoxLayout()
        
        btn_nuevo = QPushButton("Nuevo Usuario")
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

    def _load_users(self):
        """Carga los usuarios."""
        self.lista.clear()
        db = SessionLocal()
        try:
            users = db.query(User).order_by(User.username).all()
            for u in users:
                status = "✓" if u.is_active else "✗"
                role_icon = "👑" if u.role == 'admin' else "👤"
                display = f"{status} {role_icon} {u.username}"
                if u.full_name:
                    display += f" - {u.full_name}"
                display += f" ({u.role})"
                
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, u.id)
                self.lista.addItem(item)
        finally:
            db.close()

    def _on_new(self):
        """Crea un nuevo usuario."""
        dialog = UserDialog(is_new=True, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            db = SessionLocal()
            try:
                service = UserService()
                user, error = service.create(
                    db,
                    username=data['username'],
                    password=data['password'],
                    full_name=data['full_name'],
                    role=data['role']
                )
                
                if error:
                    QMessageBox.warning(self, "Error", error)
                else:
                    self._load_users()
                    QMessageBox.information(self, "Éxito", "Usuario creado correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                db.close()

    def _on_edit(self):
        """Edita el usuario seleccionado."""
        item = self.lista.currentItem()
        if not item:
            return
        
        user_id = item.data(Qt.UserRole)
        db = SessionLocal()
        try:
            user = UserRepository.get_by_id(db, user_id)
            if not user:
                return
            
            dialog = UserDialog(user=user, parent=self)
            if dialog.exec():
                data = dialog.get_data()
                
                service = UserService(current_user_id=self.current_user.id if self.current_user else None)
                user, error = service.update(
                    db, user_id,
                    full_name=data['full_name'],
                    role=data['role'],
                    is_active=data['is_active'],
                    password=data['password'] if data['password'] else None
                )
                
                if error:
                    QMessageBox.warning(self, "Error", error)
                else:
                    self._load_users()
                    QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()

    def _on_delete(self):
        """Elimina el usuario seleccionado (borrado lógico)."""
        item = self.lista.currentItem()
        if not item:
            return
        
        user_id = item.data(Qt.UserRole)
        
        confirm = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Está seguro de eliminar este usuario?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return
        
        db = SessionLocal()
        try:
            service = UserService(current_user_id=self.current_user.id if self.current_user else None)
            success, error = service.delete(db, user_id)
            
            if error:
                QMessageBox.warning(self, "Error", error)
            else:
                self._load_users()
                QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()