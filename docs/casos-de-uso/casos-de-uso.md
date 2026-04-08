# Casos de Uso

## 1. Actores del Sistema

| Actor | Descripción | Permisos |
|-------|-------------|----------|
| **Administrador** | Usuario con control total del sistema | Gestión completa de productos, stock, categorías, proveedores, usuarios |
| **Vendedor** | Usuario con acceso limitado | Solo operaciones de venta y consulta |

---

## 2. Casos de Uso - Autenticación

### CU-001: Iniciar Sesión

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-001 |
| **Nombre** | Iniciar Sesión |
| **Actor** | Administrador, Vendedor |
| **Precondición** | Usuario debe existir en el sistema |
| **Flujo Principal** | 1. Usuario ingresa username y password 2. Sistema valida credenciales 3. Sistema crea sesión |
| **Flujo Alternativo** | Si credenciales incorrectas, mostrar mensaje de error |
| **Postcondición** | Usuario autenticado con permisos asignados |

---

## 3. Casos de Uso - Productos

### CU-002: Crear Producto

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-002 |
| **Nombre** | Crear Producto |
| **Actor** | Administrador |
| **Precondición** | Estar autenticado como Administrador |
| **Flujo Principal** | 1. Seleccionar "Nuevo Producto" 2. Ingresar: código, nombre, marca, costo, precio, categoría, proveedor 3. Guardar |
| **Postcondición** | Producto creado en la base de datos |

### CU-003: Buscar Producto

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-003 |
| **Nombre** | Buscar Producto |
| **Actor** | Administrador, Vendedor |
| **Flujo Principal** | 1. Ingresar términos de búsqueda 2. Aplicar filtros 3. Ver resultados |
| **Postcondición** | Lista de productos coincidentes mostrada |

### CU-004: Editar Producto

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-004 |
| **Nombre** | Editar Producto |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Seleccionar producto 2. Modificar campos 3. Guardar |
| **Postcondición** | Producto actualizado |

### CU-005: Eliminar Producto

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-005 |
| **Nombre** | Eliminar Producto |
| **Actor** | Administrador |
| **Restricciones** | Solo si no tiene movimientos de stock |
| **Flujo Principal** | 1. Seleccionar producto 2. Confirmar eliminación 3. Producto eliminado |
| **Postcondición** | Producto marcado como inactivo |

### CU-006: Escanear Código de Barras

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-006 |
| **Nombre** | Escanear Código de Barras |
| **Actor** | Vendedor |
| **Flujo Principal** | 1. Escanear código con lector o ingresar manualmente 2. Si existe, mostrar producto 3. Si no existe, ofrecer crear nuevo |

---

## 4. Casos de Uso - Stock

### CU-007: Registrar Entrada de Stock

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-007 |
| **Nombre** | Registrar Entrada de Stock |
| **Actor** | Administrador, Vendedor |
| **Flujo Principal** | 1. Ingresar código de producto 2. Ingresar cantidad 3. Ingresar motivo 4. Confirmar |
| **Postconción** | Stock incrementado, movimiento registrado |

### CU-008: Registrar Salida de Stock

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-008 |
| **Nombre** | Registrar Salida de Stock |
| **Actor** | Vendedor |
| **Restricciones** | No puede exceder stock disponible |
| **Flujo Principal** | 1. Ingresar código de producto 2. Ingresar cantidad 3. Confirmar |
| **Validaciones** | Verificar stock suficiente |
| **Postconción** | Stock decrementado, movimiento registrado |

### CU-009: Ver Historial de Stock

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-009 |
| **Nombre** | Ver Historial de Stock |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Seleccionar producto 2. Ver historial de movimientos |
| **Postconción** | Lista de movimientos mostrada |

---

## 5. Casos de Uso - Categorías

### CU-010: Crear Categoría

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-010 |
| **Nombre** | Crear Categoría |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Ingresar nombre y descripción 2. Seleccionar categoría padre (opcional) 3. Guardar |

### CU-011: Crear Subcategoría

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-011 |
| **Nombre** | Crear Subcategoría |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Seleccionar categoría padre 2. Ingresar nombre 3. Guardar |

---

## 6. Casos de Uso - Proveedores

### CU-012: Registrar Proveedor

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-012 |
| **Nombre** | Registrar Proveedor |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Ingresar: nombre, contacto, teléfono, email, dirección 2. Guardar |

### CU-013: Editar Proveedor

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-013 |
| **Nombre** | Editar Proveedor |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Seleccionar proveedor 2. Modificar datos 3. Guardar |

---

## 7. Casos de Uso - Usuarios

### CU-014: Crear Usuario

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-014 |
| **Nombre** | Crear Usuario |
| **Actor** | Administrador |
| **Restricciones** | No puede eliminar último admin |
| **Flujo Principal** | 1. Ingresar username, nombre, rol 2. Establecer contraseña 3. Guardar |

### CU-015: Cambiar Contraseña

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-015 |
| **Nombre** | Cambiar Contraseña |
| **Actor** | Administrador, Vendedor |
| **Flujo Principal** | 1. Ingresar contraseña actual 2. Ingresar nueva contraseña 3. Confirmar |

---

## 8. Casos de Uso - Reportes

### CU-016: Ver Dashboard

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-016 |
| **Nombre** | Ver Dashboard |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Acceder al dashboard 2. Ver KPIs 3. Ver gráficos |
| **KPIs Mostrados** | Total productos, Total stock, Movimientos recientes |

### CU-017: Exportar a CSV

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-017 |
| **Nombre** | Exportar a CSV |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Seleccionar tipo de datos 2. Elegir exportar 3. Guardar archivo |

### CU-018: Exportar a Excel

| Campo | Descripción |
|-------|-------------|
| **ID** | CU-018 |
| **Nombre** | Exportar a Excel |
| **Actor** | Administrador |
| **Flujo Principal** | 1. Seleccionar tipo de datos 2. Elegir exportar 3. Guardar archivo .xlsx |

---

## 9. Diagrama de Casos de Uso (Resumen)

```
┌─────────────────────────────────────────────────────────────────┐
│                        ADMINISTRADOR                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Productos│  │  Stock   │  │Categorías │  │Proveedor │       │
│  │ - Crear  │  │ - Entrada│  │ - Crear  │  │ - Crear  │       │
│  │ - Editar │  │ - Salida │  │ - Editar │  │ - Editar │       │
│  │ - Buscar │  │ - Hist.  │  │ - Eliminar│  │ - Eliminar│       │
│  │ - Eliminar│  │          │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Usuarios │  │Dashboard │  │ Exportar │                      │
│  │ - Crear  │  │ - Ver    │  │ - CSV    │                      │
│  │ - Editar │  │          │  │ - Excel  │                      │
│  │ - Eliminar│ │          │  │          │                      │
│  │ - Permisos│ │          │  │          │                      │
│  └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          VENDEDOR                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Productos│  │  Stock   │  │ Contraseña│                      │
│  │ - Buscar │  │ - Entrada│  │ - Cambiar │                     │
│  │ - Escanear│  │ - Salida │  │          │                      │
│  └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```