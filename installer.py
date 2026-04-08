#!/usr/bin/env python3
"""
Installer interactivo para Sistema de Control de Inventario
============================================================
Instalador fácil e intuitivo que configura todo lo necesario.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*50}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def verificar_python():
    """Verifica que Python 3 esté disponible."""
    print_header("Verificando Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ requerido. Versión actual: {version.major}.{version.minor}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def verificar_dependencias():
    """Verifica e instala dependencias."""
    print_header("Verificando Dependencias")
    
    dependencias = {
        'bcrypt': 'bcrypt',
        'pandas': 'pandas', 
        'openpyxl': 'openpyxl',
        'PySide6': 'PySide6',
        'sqlalchemy': 'sqlalchemy'
    }
    
    todas_installed = True
    
    for nombre, modulo in dependencias.items():
        try:
            __import__(modulo)
            print_success(f"{nombre} instalado")
        except ImportError:
            print_warning(f"{nombre} no encontrado - requiere instalación")
            todas_installed = False
    
    if not todas_installed:
        print_info("Instalando dependencias...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print_success("Dependencias instaladas")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Error instalando dependencias: {e}")
            return False
    
    return True

def inicializar_base_datos():
    """Inicializa la base de datos."""
    print_header("Inicializando Base de Datos")
    
    # Agregar path del proyecto
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from src.database.config import init_db
        init_db()
        print_success("Base de datos inicializada")
        
        # Verificar tablas
        from src.database.config import SessionLocal
        from src.models.entities import Product, Category, Supplier, User, StockMovement
        db = SessionLocal()
        tablas = [Product, Category, Supplier, User, StockMovement]
        
        print_info("Verificando tablas:")
        for tabla in tablas:
            try:
                count = db.query(tabla).count()
                print_success(f"  {tabla.__tablename__}: {count} registros")
            except Exception as e:
                print_warning(f"  {tabla.__tablename__}: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Error inicializando base de datos: {e}")
        return False

def crear_usuario_admin(auto=False):
    """Crea el usuario administrador.
    
    Args:
        auto: Si True, crea admin con password por defecto (para --quick)
    """
    print_header("Crear Usuario Administrador")
    
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from src.database.config import SessionLocal
        from src.repository.user_repository import UserRepository
        
        db = SessionLocal()
        
        # Verificar si ya existe admin
        admin_existente = UserRepository.get_by_username(db, "admin")
        
        if admin_existente:
            print_warning("Ya existe un usuario admin")
            print_info(f"  Usuario: {admin_existente.username}")
            print_info(f"  Nombre: {admin_existente.full_name}")
            
            # En modo auto, retornar sin cambios
            if auto:
                print_info("Admin ya existe, saltando...")
                db.close()
                return True
            
            respuesta = input(f"\n{Colors.BLUE}¿Desea crear un nuevo admin? (s/n): {Colors.ENDC}").strip().lower()
            if respuesta != 's':
                print_info("Saltando creación de admin")
                db.close()
                return True
            
            respuesta_reset = input(f"{Colors.BLUE}¿Resetear contraseña del admin existente? (s/n): {Colors.ENDC}").strip().lower()
            if respuesta_reset == 's':
                from getpass import getpass
                nueva_pass = getpass("Nueva contraseña: ")
                while len(nueva_pass) < 6:
                    print_warning("La contraseña debe tener al menos 6 caracteres")
                    nueva_pass = getpass("Nueva contraseña: ")
                
                admin_existente.set_password(nueva_pass)
                db.commit()
                print_success("Contraseña actualizada")
                db.close()
                return True
        
        # ========== MODO AUTO: Crear admin con password por defecto ==========
        if auto:
            from datetime import datetime
            
            print_info("Creando usuario admin por defecto...")
            UserRepository.create(
                db,
                username="admin",
                password="admin123",
                full_name="Administrador",
                is_admin=True
            )
            print_success("Usuario 'admin' creado con contraseña por defecto: admin123")
            print()
            print(f"{Colors.WARNING}⚠ IMPORTANTE: Cambie la contraseña inmediatamente después del primer login.{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠ Para cambiar: Menú > Configuración > Cambiar Contraseña{Colors.ENDC}")
            db.close()
            return True
        
        # ========== MODO INTERACTIVO: Pedir datos ==========
        from getpass import getpass
        
        print_info("Ingrese los datos del administrador:")
        username = input("Usuario [admin]: ").strip() or "admin"
        
        # Verificar si existe
        if UserRepository.get_by_username(db, username):
            print_error(f"El usuario '{username}' ya existe")
            db.close()
            return False
        
        full_name = input("Nombre completo [Administrador]: ").strip() or "Administrador"
        
        password = getpass("Contraseña: ")
        while len(password) < 6:
            print_warning("La contraseña debe tener al menos 6 caracteres")
            password = getpass("Contraseña: ")
        
        password_confirm = getpass("Confirmar contraseña: ")
        while password != password_confirm:
            print_error("Las contraseñas no coinciden")
            password = getpass("Contraseña: ")
            password_confirm = getpass("Confirmar contraseña: ")
        
        # Crear usuario
        UserRepository.create(
            db,
            username=username,
            password=password,
            full_name=full_name,
            is_admin=True
        )
        
        print_success(f"Usuario '{username}' creado exitosamente")
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Error creando usuario: {e}")
        return False

def verificar_instalacion():
    """Verifica que todo esté correctamente instalado."""
    print_header("Verificación Final")
    
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Importar todos los módulos principales
        from src.database.config import SessionLocal, init_db
        from src.models.entities import Product, Category, Supplier, User
        from src.repository.product_repository import ProductRepository
        from src.repository.category_repository import CategoryRepository
        from src.repository.supplier_repository import SupplierRepository
        from src.repository.user_repository import UserRepository
        from src.services.product_service import ProductService
        from src.services.category_service import CategoryService
        from src.services.supplier_service import SupplierService
        from src.services.user_service import UserService
        
        print_success("Todos los módulos cargados correctamente")
        
        # Verificar admin
        db = SessionLocal()
        admin = UserRepository.get_by_username(db, "admin")
        if admin:
            print_success("Usuario admin configurado")
        else:
            print_warning("Usuario admin no encontrado")
        db.close()
        
        return True
        
    except Exception as e:
        print_error(f"Error en verificación: {e}")
        return False

def mostrar_instrucciones():
    """Muestra cómo ejecutar la aplicación."""
    print_header("¡Instalación Completada!")
    
    print(f"{Colors.GREEN}La aplicación está lista para usar.{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Para ejecutar:{Colors.ENDC}")
    print(f"  {Colors.BLUE}python3 main.py{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Credenciales por defecto:{Colors.ENDC}")
    print(f"  Usuario: admin")
    print(f"  Contraseña: admin123")
    
    print(f"\n{Colors.WARNING}⚠ IMPORTANTE: Cambia la contraseña desde la aplicación después del primer login.{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠ Para cambiar: Menú > Configuración > Cambiar Contraseña{Colors.ENDC}\n")

def menu_principal():
    """Muestra el menú principal."""
    while True:
        print_header("INSTALLER - Sistema de Control de Inventario")
        print("1. Verificar Python y dependencias")
        print("2. Inicializar base de datos")
        print("3. Crear usuario administrador")
        print("4. Verificar instalación completa")
        print("5. Ejecutar aplicación")
        print("6. Salir")
        
        opcion = input(f"\n{Colors.BOLD}Seleccione una opción: {Colors.ENDC}").strip()
        
        if opcion == '1':
            if not verificar_python():
                continue
            if not verificar_dependencias():
                print_error("Verifique que pip esté disponible")
                continue
            print_success("Python y dependencias verificados")
            
        elif opcion == '2':
            if not inicializar_base_datos():
                print_error("Error al inicializar base de datos")
                continue
            print_success("Base de datos lista")
            
        elif opcion == '3':
            if not crear_usuario_admin():
                print_error("Error al crear usuario admin")
                continue
            print_success("Administrador configurado")
            
        elif opcion == '4':
            print_info("Ejecutando verificación completa...")
            if not verificar_python():
                continue
            if not verificar_dependencias():
                continue
            if not inicializar_base_datos():
                continue
            if not verificar_instalacion():
                print_error("Verificación fallida")
                continue
            print_success("✓ Instalación verificada correctamente")
            
        elif opcion == '5':
            print_info("Ejecutando aplicación...")
            try:
                subprocess.Popen([sys.executable, 'main.py'], 
                                cwd=Path(__file__).parent)
                print_success("Aplicación iniciada")
            except Exception as e:
                print_error(f"Error ejecutando: {e}")
                
        elif opcion == '6':
            print_info("Saliendo...")
            break
            
        else:
            print_warning("Opción inválida")

def install_rapida():
    """Ejecuta instalación rápida sin interacción."""
    print_header("Instalación Rápida")
    
    # Paso 1: Python
    if not verificar_python():
        sys.exit(1)
    
    # Paso 2: Dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    # Paso 3: Base de datos
    if not inicializar_base_datos():
        sys.exit(1)
    
    # Paso 4: Admin (modo automático - password por defecto)
    crear_usuario_admin(auto=True)
    
    # Paso 5: Verificación
    if not verificar_instalacion():
        sys.exit(1)
    
    # Mostrar instrucciones
    mostrar_instrucciones()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        install_rapida()
    else:
        menu_principal()

if __name__ == "__main__":
    main()