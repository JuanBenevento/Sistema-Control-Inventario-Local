import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, 
                             QInputDialog)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QSortFilterProxyModel, Qt, QTimer, QItemSelectionModel

from src.database.config import init_db, SessionLocal
from src.services.product_service import ProductService
from src.services.stock_service import StockService
from src.repository.user_repository import UserRepository
from src.ui.inventory_model import InventoryTableModel
from src.ui.stock_history_dialog import StockHistoryDialog
from src.ui.product_edit_dialog import ProductEditDialog
from src.ui.login_dialog import LoginDialog
from src.utils.logger import get_logger
from src.controllers.inventory_controller import InventoryController


class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Logger para excepciones
        self.logger = get_logger(__name__)
        
        # Mostrar login primero
        self.current_user = None
        self.operator_name = None
        self.user_permissions = set()
        self.user_role = 'vendedor'
        if not self._show_login():
            sys.exit(0)
        
        # Acumulador de barcode para captura global
        self._barcode_buffer = ""
        self._barcode_timer = QTimer()
        self._barcode_timer.setSingleShot(True)
        self._barcode_timer.timeout.connect(self._procesar_barcode_buffer)
        
        # Timer para restaurar foco
        self._foco_timer = QTimer()
        self._foco_timer.setSingleShot(True)
        
        # Monitoreo de portapapeles para barcode-to-pc
        self._last_clipboard = ""
        self._clipboard_timer = QTimer()
        self._clipboard_timer.setSingleShot(False)
        self._clipboard_timer.timeout.connect(self._check_clipboard)
        
        # Cargar Interfaz
        loader = QUiLoader()
        ui_file = QFile("src/ui/main_view.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("Control de Stock")
        
        # Actualizar label de operador
        self._update_operador_label()
        self._restaurar_foco()
        
        # Iniciar monitoreo de portapapeles
        clipboard = QApplication.clipboard()
        self._last_clipboard = clipboard.text()
        self._clipboard_timer.start(500)
        
        # Configuración de Modelos
        self.base_model = InventoryTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.base_model)
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        self.ui.tabla_stock.setModel(self.proxy_model)
        self.ui.tabla_stock.setSortingEnabled(True)
        self.ui.tabla_stock.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        
        # Configuración Inicial
        self.ui.rb_venta.setChecked(True)
        self.ui.spn_cantidad.setValue(1)
        self._foco_timer.timeout.connect(lambda: self.ui.txt_codigo.setFocus())
        self._restaurar_foco()
        
        # Conexión de Eventos
        self.ui.txt_codigo.returnPressed.connect(self._procesar_desde_campo)
        self.ui.txt_codigo.textChanged.connect(self._on_text_changed)
        self.ui.txt_filtro.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.ui.btn_editar.clicked.connect(self.abrir_editor)
        self.ui.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.ui.btn_historial.clicked.connect(self.mostrar_historial)
        self.ui.btn_dashboard.clicked.connect(self.mostrar_dashboard)
        self.ui.btn_exportar.clicked.connect(self.mostrar_exportar)
        self.ui.btn_categorias.clicked.connect(self.mostrar_categorias)
        self.ui.btn_proveedores.clicked.connect(self.mostrar_proveedores)
        self.ui.btn_usuarios.clicked.connect(self.mostrar_usuarios)
        
        self.actualizar_tabla()
        self._update_ui_permissions()
    
    def _show_login(self):
        """Muestra el diálogo de login. Retorna True si autentica, False si cancela."""
        login = LoginDialog(self)
        if login.exec():
            self.current_user = login.user
            self.operator_name = login.operator_name
            # Guardar permisos del usuario (se aplican después de cargar UI)
            self.user_permissions = login.permissions
            self.user_role = login.user_role
            
            # Inicializar controlador de inventario
            self.controller = InventoryController(self.operator_name)
            return True
        return False
    
    def _update_operador_label(self):
        """Actualiza el label de operador en la interfaz."""
        if self.current_user:
            nombre = self.current_user.full_name or self.current_user.username
            self.ui.lbl_operador.setText(f"Usuario: {nombre}")
    
    def has_permission(self, permission: str) -> bool:
        """Verifica si el usuario actual tiene el permiso."""
        return permission in self.user_permissions or self.user_role == 'admin'
    
    def _update_ui_permissions(self):
        """Actualiza la UI según los permisos del usuario."""
        # Deshabilitar gestión de usuarios si no es admin
        if not self.has_permission('user.manage'):
            if hasattr(self.ui, 'btn_usuarios'):
                self.ui.btn_usuarios.setEnabled(False)
    
    def _restaurar_foco(self):
        """Restaura el foco al campo de código."""
        self._foco_timer.start(100)
    
    def keyPressEvent(self, event):
        """Captura global de teclas para recibir barcodes."""
        key = event.key()
        text = event.text()
        
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            if self._barcode_buffer:
                self._barcode_timer.stop()
                self._procesar_barcode_buffer()
            super().keyPressEvent(event)
            return
        
        if key == Qt.Key_Backspace:
            self._barcode_buffer = self._barcode_buffer[:-1]
            super().keyPressEvent(event)
            return
        
        if text and text.isprintable():
            self._barcode_buffer += text
            self._barcode_timer.start(50)
            return
        
        super().keyPressEvent(event)
    
    def _on_text_changed(self, text):
        """Si el usuario escribe manualmente, sincronizar buffer."""
        if len(text) > len(self._barcode_buffer):
            self._barcode_buffer = text
    
    def _check_clipboard(self):
        """Monitorea el portapapeles para detectar barcodes de barcode-to-pc."""
        try:
            clipboard = QApplication.clipboard()
            current = clipboard.text()
            
            if current and current != self._last_clipboard:
                self._last_clipboard = current
                stripped = current.strip()
                if stripped and len(stripped) < 100 and self._looks_like_barcode(stripped):
                    self._procesar_barcode(stripped)
                    clipboard.setText("")
                    self._last_clipboard = ""
        except Exception as e:
            self.logger.warning(f"Error procesando clipboard: {e}")
    
    def _looks_like_barcode(self, text):
        """Determina si el texto parece un barcode válido."""
        if len(text) < 4 or len(text) > 50:
            return False
        if ' ' in text and '\n' not in text:
            return False
        return True
    
    def _procesar_desde_campo(self):
        """Procesa el barcode desde el campo de texto."""
        barcode = self.ui.txt_codigo.text().strip()
        if barcode:
            self._barcode_buffer = ""
            self._procesar_barcode(barcode)
            self.ui.txt_codigo.clear()
            self._restaurar_foco()
    
    def _procesar_barcode_buffer(self):
        """Procesa el barcode acumulado desde captura global."""
        if self._barcode_buffer:
            barcode = self._barcode_buffer.strip()
            self._barcode_buffer = ""
            if barcode:
                self.ui.txt_codigo.setText(barcode)
                self._procesar_barcode(barcode)
                self.ui.txt_codigo.clear()
                self._restaurar_foco()
    
    def _procesar_barcode(self, barcode):
        """Procesa un barcode - busca o crea producto."""
        db = SessionLocal()
        try:
            modo = "IN" if self.ui.rb_ingreso.isChecked() else "OUT"
            
            # Si es IN, buscar también productos inactivos
            if modo == "IN":
                product = ProductService.get_by_barcode(db, barcode, only_active=False)
                if product and not getattr(product, 'is_active', True):
                    # Producto inactivo encontrado - preguntamos si desea reactivarlo
                    respuesta = QMessageBox.question(
                        self,
                        "Producto Inactivo",
                        f"El producto '{product.name}' está dado de baja.\n\n"
                        f"¿Desea reactivarlo y registrar el ingreso?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if respuesta == QMessageBox.Yes:
                        cantidad = self.ui.spn_cantidad.value()
                        # Registrar el movimiento de stock
                        from src.models.entities import StockMovement
                        movement = StockMovement(
                            product_id=product.id,
                            type="IN",
                            quantity=cantidad,
                            user_name=self.operator_name
                        )
                        db.add(movement)
                        # Actualizar stock
                        product.stock_qty += cantidad
                        # Reactivar
                        product.is_active = True
                        db.commit()
                        db.refresh(product)
                        
                        self.actualizar_tabla()
                        self._seleccionar_producto(product.id)
                        self.ui.lbl_mensaje.setText(f"Reactivado: {product.name} (+{cantidad})")
                        self.ui.lbl_mensaje.setStyleSheet("color: blue; font-weight: bold;")
                    return
            else:
                # Si es OUT, solo buscar activos
                product = ProductService.get_by_barcode(db, barcode)

            if product:
                self.modificar_stock(db, product, modo)
                self._seleccionar_producto(product.id)
            else:
                self.nuevo_producto(db, barcode, modo)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Falla: {str(e)}")
        finally:
            db.close()
    
    def _seleccionar_producto(self, product_id):
        """Selecciona automáticamente un producto en la tabla por su ID."""
        for row, prod in enumerate(self.base_model._data):
            if prod.id == product_id:
                index = self.proxy_model.mapFromSource(self.base_model.index(row, 0))
                self.ui.tabla_stock.selectionModel().clear()
                self.ui.tabla_stock.selectionModel().select(index, QItemSelectionModel.Select)
                self.ui.tabla_stock.scrollTo(index)
                break
    
    def _obtener_producto_seleccionado(self):
        """Obtiene el producto seleccionado o None si no hay selección."""
        seleccion = self.ui.tabla_stock.selectionModel().selectedRows()
        if not seleccion:
            return None
        proxy_index = seleccion[0]
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self.base_model._data[source_index.row()]
    
    def _on_header_clicked(self, logical_index):
        """Handle header click for sorting."""
        current_order = self.ui.tabla_stock.horizontalHeader().sortIndicatorOrder()
        new_order = Qt.DescendingOrder if current_order == Qt.AscendingOrder else Qt.AscendingOrder
        self.base_model.sort(logical_index, new_order)
    
    def actualizar_tabla(self):
        db = SessionLocal()
        try:
            from src.models.entities import Product
            productos = db.query(Product).order_by(Product.name).all()
            self.base_model.update_data(productos)
            self.ui.lbl_mensaje.setText("Listo para escanear...")
            self.ui.lbl_mensaje.setStyleSheet("color: #555;")
        finally:
            db.close()
    
    def modificar_stock(self, db, product, modo):
        cantidad = self.ui.spn_cantidad.value()
        
        if modo == "OUT" and product.stock_qty < cantidad:
            self.ui.lbl_mensaje.setText(f"STOCK INSUFICIENTE: {product.name} (disponible: {product.stock_qty})")
            self.ui.lbl_mensaje.setStyleSheet("color: red; font-weight: bold;")
            self._restaurar_foco()
            return

        if modo == "IN":
            StockService.record_in(db, product.id, cantidad, self.operator_name)
            mensaje = f"OK: {product.name} (INGRESO) +{cantidad}"
        else:
            StockService.record_out(db, product.id, cantidad, self.operator_name)
            mensaje = f"OK: {product.name} (VENTA) -{cantidad}"
        
        # Obtener producto fresco para verificar alertas
        from src.models.entities import Product
        product_fresh = db.get(Product, product.id)
        
        self.ui.lbl_mensaje.setText(mensaje)
        self.ui.lbl_mensaje.setStyleSheet("color: green; font-weight: bold;")
        self.actualizar_tabla()
        if product_fresh:
            self._verificar_alerta_stock(product_fresh)

    def abrir_editor(self):
        """Edita el producto seleccionado con formulario dedicado."""
        producto = self._obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Atención", 
                "Seleccione un producto en la tabla\no escanee un código de barras.")
            return
        
        db = SessionLocal()
        try:
            # Obtener producto fresco desde la BD
            from src.models.entities import Product
            producto_db = db.get(Product, producto.id)
            if not producto_db:
                QMessageBox.critical(self, "Error", "Producto no encontrado en la base de datos.")
                return
            
            dialog = ProductEditDialog(producto_db, self)
            if dialog.exec():
                datos = dialog.get_data()
                
                ProductService.update_product(
                    db, 
                    producto.id,
                    name=datos["name"],
                    brand=datos["brand"],
                    cost_usd=datos["cost_usd"],
                    sale_price=datos["sale_price"],
                    min_stock_alert=datos["min_stock_alert"],
                    category_id=datos.get("category_id"),
                    supplier_id=datos.get("supplier_id"),
                )
                self.ui.lbl_mensaje.setText(f"Actualizado: {datos['name']}")
                self.ui.lbl_mensaje.setStyleSheet("color: green; font-weight: bold;")
                self.actualizar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
        finally:
            db.close()

    def eliminar_producto(self):
        """Da de baja o alta el producto seleccionado según su estado."""
        producto = self._obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Atención", 
                "Seleccione un producto en la tabla\no escanee un código de barras.")
            return

        db = SessionLocal()
        try:
            is_active = getattr(producto, 'is_active', True)
            
            if is_active:
                # Producto activo → intentar dar de baja
                if producto.stock_qty > 0:
                    QMessageBox.warning(
                        self, 
                        "No se puede dar de baja",
                        f"El producto '{producto.name}' tiene stock: {producto.stock_qty}\n\n"
                        f"Para darlo de baja, primero debe vender o retirar todo el stock."
                    )
                    return
                
                confirmar = QMessageBox.question(
                    self, 
                    "Dar de Baja", 
                    f"¿Dar de baja '{producto.name}'?\n\n"
                    f"Podrá darlo de alta nuevamente cuando tenga stock.",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if confirmar == QMessageBox.Yes:
                    result, error = ProductService.deactivate(db, producto.id)
                    if error:
                        QMessageBox.critical(self, "Error", error)
                    else:
                        self.ui.lbl_mensaje.setText(f"Dado de baja: {producto.name}")
                        self.ui.lbl_mensaje.setStyleSheet("color: orange; font-weight: bold;")
                        self.actualizar_tabla()
            
            else:
                # Producto inactivo → intentar dar de alta
                if producto.stock_qty <= 0:
                    QMessageBox.warning(
                        self, 
                        "No se puede dar de alta",
                        f"El producto '{producto.name}' tiene stock: {producto.stock_qty}\n\n"
                        f"Para darlo de alta, primero debe registrar un ingreso de stock."
                    )
                    return
                
                confirmar = QMessageBox.question(
                    self, 
                    "Dar de Alta", 
                    f"¿Dar de alta '{producto.name}'?\n\n"
                    f"Stock actual: {producto.stock_qty}",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if confirmar == QMessageBox.Yes:
                    result, error = ProductService.activate(db, producto.id)
                    if error:
                        QMessageBox.critical(self, "Error", error)
                    else:
                        self.ui.lbl_mensaje.setText(f"Dado de alta: {producto.name}")
                        self.ui.lbl_mensaje.setStyleSheet("color: green; font-weight: bold;")
                        self.actualizar_tabla()
        finally:
            db.close()

    def nuevo_producto(self, db, barcode, modo):
        """Crea un nuevo producto con el barcode dado usando formulario."""
        from src.models.entities import Product
        dummy = Product()
        dummy.barcode = barcode
        dummy.name = ""
        dummy.brand = ""
        dummy.cost_usd = 0.0
        dummy.sale_price = 0.0
        dummy.stock_qty = 0
        dummy.min_stock_alert = 2
        
        dialog = ProductEditDialog(dummy, self)
        if dialog.exec():
            datos = dialog.get_data()
            
            cantidad = self.ui.spn_cantidad.value() if modo == "IN" else 0
            
            # Crear el producto (si hay cantidad inicial, create_product ya lo registra)
            nuevo = ProductService.create_product(
                db,
                barcode=datos["barcode"],
                name=datos["name"],
                brand=datos["brand"],
                cost_usd=datos["cost_usd"],
                sale_price=datos["sale_price"],
                initial_stock=cantidad,
                min_stock_alert=datos["min_stock_alert"],
                category_id=datos.get("category_id"),
                supplier_id=datos.get("supplier_id"),
            )
            
            # Sincronizar con la BD y actualizar tabla
            self.actualizar_tabla()
            self._seleccionar_producto(nuevo.id)
            
            self.ui.lbl_mensaje.setText(f"Producto creado: {datos['name']}")
            self.ui.lbl_mensaje.setStyleSheet("color: green; font-weight: bold;")
            
            # Verificar alerta de stock bajo
            if cantidad > 0 and cantidad <= datos["min_stock_alert"]:
                self._verificar_alerta_stock(nuevo)

    def _verificar_alerta_stock(self, product):
        """Check if product stock is at or below min_stock_alert threshold."""
        if product.stock_qty <= product.min_stock_alert:
            QMessageBox.warning(
                self,
                "¡Alerta! Stock Bajo",
                f"Stock bajo: {product.name}\n"
                f"Stock actual: {product.stock_qty}\n"
                f"Umbral mínimo: {product.min_stock_alert}"
            )
            self._restaurar_foco()

    def mostrar_historial(self):
        """Muestra el historial del producto seleccionado."""
        producto = self._obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Atención", 
                "Seleccione un producto en la tabla\no escanee un código de barras.")
            return

        db = SessionLocal()
        try:
            # Obtener producto fresco desde la BD
            from src.models.entities import Product
            producto_db = db.get(Product, producto.id)
            if not producto_db:
                QMessageBox.critical(self, "Error", "Producto no encontrado.")
                return
            dialog = StockHistoryDialog(producto_db, db, self)
            dialog.exec()
        finally:
            db.close()

    def mostrar_dashboard(self):
        """Muestra el dashboard en un diálogo."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
        from src.ui.dashboard_view import DashboardView
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Dashboard")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        dashboard = DashboardView()
        layout.addWidget(dashboard)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(dialog.accept)
        layout.addWidget(btn_cerrar)
        
        dialog.exec()

    def mostrar_exportar(self):
        """Muestra el diálogo de exportación."""
        from src.ui.export_dialog import ExportDialog
        dialog = ExportDialog(self)
        dialog.exec()

    def mostrar_categorias(self):
        """Muestra el diálogo de gestión de categorías."""
        from src.ui.category_dialog import CategoryManagerDialog
        from src.models.permissions import ROLES
        
        if hasattr(self.current_user, 'is_admin') and self.current_user.is_admin:
            user_perms = ROLES['admin']
        else:
            user_perms = ROLES.get('vendedor', set())
        
        dialog = CategoryManagerDialog(self, user_permissions=user_perms)
        dialog.exec()

    def mostrar_proveedores(self):
        """Muestra el diálogo de gestión de proveedores."""
        from src.ui.supplier_dialog import SupplierManagerDialog
        from src.models.permissions import ROLES
        
        if self.current_user.is_admin:
            user_perms = ROLES['admin']
        else:
            user_perms = ROLES.get('vendedor', set())
        
        dialog = SupplierManagerDialog(self, user_permissions=user_perms)
        dialog.exec()
    
    def mostrar_usuarios(self):
        """Muestra el diálogo de gestión de usuarios (solo admin)."""
        if not self.has_permission('user.manage'):
            QMessageBox.warning(self, "Acceso denegado", 
                "No tienes permisos para gestionar usuarios.")
            return
        
        from src.ui.user_dialog import UserManagerDialog
        dialog = UserManagerDialog(self, user_permissions=self.user_permissions, current_user=self.current_user)
        dialog.exec()


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec())
