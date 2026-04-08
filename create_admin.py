#!/usr/bin/env python3
"""Script para crear el usuario administrador inicial."""

import sys
import os
from getpass import getpass

sys.path.insert(0, '.')

from src.database.config import init_db, SessionLocal
from src.repository.user_repository import UserRepository


def obtener_password():
    """Obtiene la contraseña del admin desde variable de entorno o input."""
    # Intentar desde variable de entorno
    if 'ADMIN_PASSWORD' in os.environ:
        password = os.environ['ADMIN_PASSWORD']
        if len(password) >= 6:
            return password
        else:
            print("ADVERTENCIA: La variable ADMIN_PASSWORD es muy短 (< 6 caracteres)")
    
    # Pedir por input interactivo
    while True:
        password = getpass("Ingrese contraseña para admin: ")
        if len(password) < 6:
            print("ADVERTENCIA: La contraseña debe tener al menos 6 caracteres")
            continue
        break
    
    return password


def crear_usuario_admin():
    """Crea el usuario administrador si no existe."""
    init_db()
    
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        admin = UserRepository.get_by_username(db, "admin")
        if admin:
            print(f"Ya existe un usuario admin: {admin.username}")
            print(f"Nombre: {admin.full_name}")
            print(f"Es admin: {admin.is_admin}")
            return
        
        # Crear admin con password dinámica
        password = obtener_password()
        user = UserRepository.create(
            db,
            username="admin",
            password=password,
            full_name="Administrador",
            is_admin=True
        )
        print(f"Usuario administrador creado exitosamente!")
        print(f"Usuario: admin")
        print(f"Contraseña: [configurada]")
        print(f"\nIMPORTANTE: Cambie la contraseña inmediatamente después del primer login.")
        
    except Exception as e:
        print(f"Error al crear usuario: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    crear_usuario_admin()
