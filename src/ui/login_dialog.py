from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                              QLabel, QLineEdit, QPushButton, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.database.config import SessionLocal
from src.repository.user_repository import UserRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LoginDialog(QDialog):
    """Dialogo de login profesional con diseño moderno."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_data = None
        self.setWindowTitle("Control de Stock - Login")
        self.setFixedSize(400, 320)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self._setup_ui()
    
    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header con gradiente
        header_widget = QWidget()
        header_widget.setFixedHeight(100)
        header_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #2c3e50, stop:1 #3498db);
        """)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Control de Stock")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Gestión de Inventario")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: rgba(255,255,255,180);")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_widget)
        
        # Formulario
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(40, 30, 40, 20)
        
        # Usuario
        user_label = QLabel("USUARIO")
        user_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        user_label.setStyleSheet("color: #555;")
        form_layout.addWidget(user_label)
        
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Ingrese su usuario")
        self.txt_usuario.setFont(QFont("Segoe UI", 12))
        self.txt_usuario.setMinimumHeight(42)
        self.txt_usuario.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 8px 12px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.txt_usuario.returnPressed.connect(self._on_login)
        form_layout.addWidget(self.txt_usuario)
        
        # Contraseña
        pass_label = QLabel("CONTRASEÑA")
        pass_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        pass_label.setStyleSheet("color: #555;")
        form_layout.addWidget(pass_label)
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Ingrese su contraseña")
        self.txt_password.setFont(QFont("Segoe UI", 12))
        self.txt_password.setMinimumHeight(42)
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 8px 12px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.txt_password.returnPressed.connect(self._on_login)
        form_layout.addWidget(self.txt_password)
        
        # Mensaje de error
        self.lbl_error = QLabel()
        self.lbl_error.setFont(QFont("Segoe UI", 10))
        self.lbl_error.setStyleSheet("color: #e74c3c; background: #fdeaea; padding: 10px; border-radius: 5px;")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setVisible(False)
        self.lbl_error.setFixedHeight(45)
        form_layout.addWidget(self.lbl_error)
        
        # Botón entrar
        self.btn_login = QPushButton("INICIAR SESIÓN")
        self.btn_login.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_login.setMinimumHeight(45)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #21618c;
            }
        """)
        self.btn_login.clicked.connect(self._on_login)
        form_layout.addWidget(self.btn_login)
        
        main_layout.addWidget(form_widget)
        
        self.setLayout(main_layout)
    
    def _on_login(self):
        """Valida las credenciales."""
        username = self.txt_usuario.text().strip()
        password = self.txt_password.text()
        
        if not username:
            self._show_error("Ingrese el nombre de usuario")
            self.txt_usuario.setFocus()
            return
        
        if not password:
            self._show_error("Ingrese la contraseña")
            self.txt_password.setFocus()
            return
        
        db = SessionLocal()
        try:
            user = UserRepository.authenticate(db, username, password)
            if user:
                # Guardar datos antes de cerrar sesión
                role = getattr(user, 'role', 'vendedor')
                
                # Obtener permisos del rol
                from src.models.permissions import ROLES
                permissions = ROLES.get(role, ROLES.get('vendedor', set()))
                
                self._user_data = {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'is_admin': user.is_admin,
                    'role': role,
                    'permissions': permissions
                }
                logger.info(f"Login exitoso: {username}")
                self.accept()
            else:
                logger.warning(f"Login fallido: usuario={username}")
                self._show_error("Usuario o contraseña incorrectos")
                self.txt_password.clear()
                self.txt_password.setFocus()
        except Exception as e:
            logger.error(f"Error en login: {e}", exc_info=True)
            self._show_error("Error de conexión")
        finally:
            db.close()
    
    @property
    def user(self):
        """Retorna un objeto simple con los datos del usuario (sin sesión)."""
        class UserData:
            def __init__(self, data):
                self.id = data['id']
                self.username = data['username']
                self.full_name = data['full_name']
                self.is_admin = data['is_admin']
        
        if self._user_data:
            return UserData(self._user_data)
        return None
    
    @property
    def operator_name(self):
        """Retorna el nombre del operador para mostrar en la UI."""
        if self._user_data:
            return self._user_data['full_name'] or self._user_data['username']
        return None
    
    @property
    def permissions(self):
        """Retorna los permisos del usuario."""
        if self._user_data:
            return self._user_data.get('permissions', set())
        return set()
    
    @property
    def user_role(self):
        """Retorna el rol del usuario."""
        if self._user_data:
            return self._user_data.get('role', 'vendedor')
        return 'vendedor'
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.lbl_error.setText(message)
        self.lbl_error.setVisible(True)
