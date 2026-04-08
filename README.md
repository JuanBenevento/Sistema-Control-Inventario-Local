# Sistema de Control de Inventario

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-green)](https://www.qt.io/qt-for-python)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange)](https://www.sqlalchemy.org/)

Sistema de gestión de inventario genérico con control de stock, ventas, categorías, proveedores y usuarios.

## ✨ Características

- **Gestión de Productos**: Crear, editar, eliminar productos con código de barras
- **Control de Stock**: Entradas y salidas de inventario con historial
- **Categorías**: Sistema de categorías con soporte para subcategorías
- **Proveedores**: Gestión de proveedores con información de contacto
- **Usuarios y Permisos**: Sistema de roles (admin, vendedor) con permisos granulares
- **Dashboard**: KPIs y métricas en tiempo real (ventas, stock, productos)
- **Exportación**: Exportar datos a CSV y Excel
- **Búsqueda Avanzada**: Filtros múltiples para encontrar productos rápido

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/inventory_system.git
   cd inventory_system
   ```

2. **Crear entorno virtual** (recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # O en Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar el instalador** (configura la DB y crea usuario admin):
   ```bash
   python3 installer.py
   ```

   O instalación rápida:
   ```bash
   python3 installer.py --quick
   ```

5. **Ejecutar la aplicación**:
   ```bash
   python3 main.py
   ```

### Credenciales por Defecto

- **Usuario**: `admin`
- **Contraseña**: La que configuraste durante la instalación

> ⚠️ **IMPORTANTE**: Cambia la contraseña desde la aplicación después del primer login.

## 📁 Estructura del Proyecto

```
inventory_system/
├── main.py                 # Punto de entrada de la aplicación
├── installer.py            # Instalador interactivo
├── create_admin.py         # Script para crear usuario admin
├── requirements.txt        # Dependencias del proyecto
├── pytest.ini              # Configuración de tests
├── .env.example            # Variables de entorno (plantilla)
│
├── src/
│   ├── config.py           # Configuración centralizada
│   ├── database/           # Configuración de base de datos
│   ├── models/             # Entidades SQLAlchemy
│   ├── repository/         # Capa de acceso a datos
│   ├── services/           # Lógica de negocio
│   ├── controllers/        # Controladores
│   ├── ui/                 # Interfaz de usuario (PySide6)
│   └── utils/              # Utilidades (auth, logger)
│
├── tests/                  # Tests automatizados
├── migrations/             # Migraciones de base de datos
├── data/                   # Base de datos SQLite
├── logs/                   # Archivos de log
└── docs/                   # Documentación
```

## 🔧 Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y ajusta los valores:

```env
ENV=dev
DB_PATH=data/inventory.db
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
UI_THEME=system
UI_LANGUAGE=es
```

### Niveles de Entorno

- `dev`: Desarrollo (logs detallados, bcrypt rounds bajos)
- `prod`: Producción (logs JSON, bcrypt rounds altos)

## 🧪 Tests

Ejecutar los tests:
```bash
python3 -m pytest tests/ -v
```

Con coverage:
```bash
python3 -m pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentación

La documentación detallada está en la carpeta `docs/`:

- [Visión y Alcance](docs/vision-y-alcance.md)
- [Requerimientos](docs/requerimientos/)
- [Casos de Uso](docs/casos-de-uso/)
- [Arquitectura](docs/arquitectura/)

## 🤝 Contribuir

1. Haz un fork del proyecto
2. Crea una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👤 Autor

Juan Manuel Benevento - [GitHub](https://github.com/JuanBnevento)

