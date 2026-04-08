# Visión y Alcance del Proyecto

## 1. Información del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre del Proyecto** | Sistema de Control de Inventario |
| **Versión** | 1.0.0 |
| **Tipo** | Aplicación de escritorio (Python/PySide6) |
| **Fecha** | Abril 2026 |

---

## 2. Visión del Producto

### 2.1 Problema que Resuelve

Los pequeños y medianos negocios requieren un sistema de gestión de inventario que les permita:

- Controlar el stock de productos de forma eficiente
- Registrar ventas y entradas/salidas de inventario
- Gestionar múltiples categorías y subcategorías de productos
- Administrar proveedores
- Manejar usuarios con diferentes niveles de acceso

### 2.2 Visión del Producto

**Sistema de Control de Inventario** es una aplicación de escritorio diseñada para pequeños y medianos negocios que necesitan un control eficiente de su inventario, ventas y proveedores, sin requerir infraestructura compleja.

> *"Facilitar la gestión de inventario con una herramienta intuitiva, segura y confiable que permita controlar stock, ventas y proveedores en un solo lugar."*

---

## 3. Alcance del Proyecto

### 3.1 Funcionalidades Incluidas (Alcance)

#### Módulo de Productos
- [x] Crear productos con código de barras, nombre, marca, precio
- [x] Editar y eliminar productos
- [x] Búsqueda avanzada con filtros múltiples
- [x] Alertas de stock mínimo

#### Módulo de Stock
- [x] Registro de entradas de inventario
- [x] Registro de salidas/ventas
- [x] Historial de movimientos de stock
- [x] Control de stock insuficiente

#### Módulo de Categorías
- [x] Crear categorías y subcategorías
- [x] Editar y eliminar categorías
- [x] Asociar productos a categorías

#### Módulo de Proveedores
- [x] Registro de proveedores
- [x] Información de contacto (teléfono, email, dirección)
- [x] Editar y eliminar proveedores

#### Módulo de Usuarios
- [x] Sistema de autenticación (login)
- [x] Roles: Administrador y Vendedor
- [x] Permisos granulares por funcionalidad
- [x] Cambio de contraseña

#### Módulo de Reportes
- [x] Dashboard con KPIs (productos, stock, movimientos)
- [x] Exportación a CSV y Excel

### 3.2 Funcionalidades Excluidas (Fuera de Alcance)

| Funcionalidad | Razón |
|---------------|-------|
| Sistema de facturación electrónica | Requiere integración con Hacienda |
| Punto de venta (POS) con impresora | Fuera del alcance inicial |
| Sincronización cloud / multi-dispositivo | Requiere backend |
| Gestión de clientes (CRM) | Puede agregarse en v2.0 |
| Reportes avanzados y gráficos | Dashboard básico en v1.0 |
| Código de barras con lector USB | Solo código manual en v1.0 |

### 3.3 Versiones Futuras (Roadmap)

| Versión | Funcionalidades Planeadas |
|---------|---------------------------|
| v1.1 | Exportar a PDF, más métricas en dashboard |
| v1.2 | Soporte para lector de código de barras |
| v2.0 | Sistema de facturación, sincronización cloud |

---

## 4. Supuestos y Dependencias

### 4.1 Supuestos

1. El sistema será usado por 1-5 usuarios simultáneamente
2. La base de datos SQLite es suficiente (no requiere MySQL/PostgreSQL)
3. Los usuarios tienen conocimientos básicos de computación
4. La aplicación correrá en Windows o Linux

### 4.2 Dependencias Técnicas

| Dependencia | Versión Mínima | Propósito |
|-------------|---------------|-----------|
| Python | 3.8+ | Runtime |
| PySide6 | 6.0+ | Interfaz gráfica |
| SQLAlchemy | 2.0+ | ORM de base de datos |
| bcrypt | 4.0+ | Hash de contraseñas |
| pandas | 2.0+ | Exportación a Excel |
| openpyxl | 3.0+ | Manipulación Excel |

---

## 5. Riesgos Identificados

| Riesgo | Impacto | Mitigación |
|--------|---------|-------------|
| Concurrencia (varios usuarios) | Medio | SQLite maneja bien few users |
| Pérdida de datos | Alto | SQLite hace backups fácil |
| Acceso no autorizado | Alto | bcrypt + permisos granulares |
| Escalabilidad | Medio | Arquitectura permite migrar a PostgreSQL |

---

## 6. Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos Python | ~50 |
| Líneas de código | ~4,500 |
| Tests automatizados | 38 |
| Coverage | 35% |
| Módulos principales | 7 (UI, Services, Repositories, Models, Controllers, Utils, Database) |

---

## 7. Licencia

Este proyecto está bajo **Licencia MIT** - ver archivo [LICENSE](LICENSE) para detalles.