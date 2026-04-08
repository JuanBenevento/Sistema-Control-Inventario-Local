#!/usr/bin/env python3
"""Migración para agregar campo is_active a productos."""

import sys
sys.path.insert(0, '.')

from src.database.config import init_db, SessionLocal
from sqlalchemy import text


def migrate():
    """Agrega columna is_active a la tabla products."""
    init_db()
    db = SessionLocal()
    
    try:
        # Verificar si la columna ya existe
        result = db.execute(text("PRAGMA table_info(products)"))
        columns = [row[1] for row in result]
        
        if 'is_active' in columns:
            print("La columna 'is_active' ya existe.")
            return
        
        # Agregar la columna
        db.execute(text("ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT 1"))
        db.commit()
        print("Migración completada: columna 'is_active' agregada.")
        print("Todos los productos existentes están ahora activos.")
        
    except Exception as e:
        print(f"Error en migración: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
