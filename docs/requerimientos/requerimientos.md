# Requerimientos del Sistema

## 1. Requerimientos Funcionales

### 1.1 Gestión de Productos

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| RF-001 | El sistema debe permitir crear productos con: código de barras, nombre, marca, costo, precio de venta, stock inicial, stock mínimo de alerta | Alta |
| RF-002 | El sistema debe permitir editar la información de un producto | Alta |
| RF-003 | El sistema debe permitir eliminar productos (solo si no tienen movimientos) | Media |
| RF-004 | El sistema debe permitir buscar productos por código, nombre, marca, categoría | Alta |
| RF-005 | El sistema debe mostrar alertas cuando el stock esté por debajo del mínimo | Alta |
| RF-006 | El sistema debe permitir activar/desactivar productos | Media |

### 1.2 Gestión de Stock

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| RF-007 | El sistema debe registrar entradas de inventario con cantidad y motivo | Alta |
| RF-008 | El sistema debe registrar salidas de inventario (ventas) con cantidad y motivo | Alta |
| RF-009 | El sistema debe impedir salidas mayores al stock disponible | Alta |
| RF-010 | El sistema debe mantener historial de todos los movimientos de stock | Alta |
| RF-011 | El sistema debe mostrar el historial de movimientos de un producto | Media |

### 1.3 Gestión de Categorías

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| RF-012 | El sistema debe permitir crear categorías | Alta |
| RF-013 | El sistema debe permitir crear subcategorías (categorías dentro de otras) | Alta |
| RF-014 | El sistema debe permitir editar categorías | Media |
| RF-015 | El sistema debe permitir eliminar categorías (solo si no tienen productos ni hijos) | Media |
| RF-016 | El sistema debe permitir asignar productos a categorías | Alta |

### 1.4 Gestión de Proveedores

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| RF-017 | El sistema debe permitir registrar proveedores con: nombre, contacto, teléfono, email, dirección, notas | Alta |
| RF-018 | El sistema debe permitir editar información de proveedores | Media |
| RF-019 | El sistema debe permitir eliminar proveedores (solo si no tienen productos asociados) | Media |
| RF-020 | El sistema debe permitir asociar productos a proveedores | Alta |

### 1.5 Gestión de Usuarios

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| RF-021 | El sistema debe autenticar usuarios con username y contraseña | Alta |
| RF-022 | El sistema debe soportar dos roles: Administrador y Vendedor | Alta |
| RF-023 | El Administrador debe poder gestionar usuarios (crear, editar, eliminar) | Alta |
| RF-024 | Los Vendedores no deben poder acceder a gestión de usuarios | Alta |
| RF-025 | El sistema debe permitir cambiar contraseña | Media |
| RF-026 | Las contraseñas deben almacenarse de forma segura (bcrypt) | Alta |

### 1.6 Reportes y Exportación

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| RF-027 | El sistema debe mostrar un dashboard con KPIs básicos | Alta |
| RF-028 | El dashboard debe mostrar: total productos, total stock, movimientos recientes | Alta |
| RF-029 | El sistema debe exportar datos a formato CSV | Media |
| RF-030 | El sistema debe exportar datos a formato Excel | Media |

---

## 2. Requerimientos No Funcionales

### 2.1 Rendimiento

| ID | Requerimiento | Criterio |
|----|---------------|----------|
| RNF-001 | Tiempo de inicio | < 5 segundos |
| RNF-001 | Búsqueda de productos | < 1 segundo |
| RNF-003 | Guardar producto | < 2 segundos |

### 2.2 Seguridad

| ID | Requerimiento | Criterio |
|----|---------------|----------|
| RNF-004 | Almacenamiento de contraseñas | bcrypt con salt |
| RNF-005 | Control de acceso | Permisos granulares por rol |
| RNF-006 | Sesiones | No hay sesión persistente (login cada vez) |

### 2.3 Usabilidad

| ID | Requerimiento | Criterio |
|----|---------------|----------|
| RNF-007 | Interfaz intuitiva | Ventanas claras y bien organizadas |
| RNF-008 | Validaciones | Mensajes de error claros |
| RNF-009 | Atajos | Soporte para escáner de código de barras |

### 2.4 Mantenibilidad

| ID | Requerimiento | Criterio |
|----|---------------|----------|
| RNF-010 | Arquitectura | Capas: UI → Controllers → Services → Repositories |
| RNF-011 | Código | Documentado, pruebas unitarias |
| RNF-012 | Configuración | Variables de entorno para configuración |

---

## 3. Reglas de Negocio

| ID | Regla | Descripción |
|----|-------|-------------|
| RN-001 | Stock mínimo | El stock mínimo de alerta es configurable por producto |
| RN-002 | Precio de venta | Debe ser mayor o igual al costo |
| RN-003 | Stock negativo | El stock no puede ser negativo |
| RN-004 | Única categoría padre | Una categoría solo puede tener un padre |
| RN-005 | Usuario único | El nombre de usuario debe ser único |
| RN-006 | Al menos un admin | Siempre debe existir al menos un usuario administrador activo |
| RN-007 | Auto-eliminación | Un usuario no puede eliminarse a sí mismo |

---

## 4. Matriz de Trazabilidad

| Requerimiento | Módulo | Test |
|---------------|--------|------|
| RF-001 a RF-006 | Products | test_product_service.py |
| RF-007 a RF-011 | Stock | test_stock_service.py |
| RF-012 a RF-016 | Categories | test_category_service.py |
| RF-017 a RF-020 | Suppliers | test_supplier_service.py |
| RF-021 a RF-026 | Users | test_auth.py |
| RF-027 a RF-030 | Reports | test_dashboard.py |