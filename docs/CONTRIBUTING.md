# Guía de Contribución

¡Gracias por tu interés en contribuir al Sistema de Inventario de Perfumería!

## 1. Código de Conducta

Por favor, sé respetuoso y profesional. Todos los contribuciones deben seguir un comportamiento ético y constructivo.

---

## 2. Cómo Contribuir

### 2.1 Reportar Bugs

Si encuentras un bug:

1. Verifica que no haya sido reportado antes
2. Crea un issue con:
   - Título claro (ej: "Bug: Login falla con contraseña correcta")
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Tu entorno (OS, Python version)

### 2.2 Sugerir Funcionalidades

Para nuevas funcionalidades:

1. Crea un issue con标签 "enhancement"
2. Describe el problema que resolvería
3. Propón una solución
4. Explica el beneficio para usuarios

### 2.3 Pull Requests

Para contribuir código:

1. **Fork** el repositorio
2. Crea una rama: `git checkout -b feature/tu-feature`
3. Haz tus cambios siguiendo las convenciones
4. Agrega tests si es posible
5. Commit con mensajes claros:
   ```
   feat: agregar filtro por categoría en búsqueda
   fix: corregir error de stock negativo
   refactor: extraer InventoryController de main.py
   ```
6. Push a tu fork
7. Crea un Pull Request

---

## 3. Estándares de Código

### 3.1 Convenciones Python

- Sigue **PEP 8**
- Usa **type hints** cuando sea posible
- Maximum línea: **100 caracteres**
- Nombres descriptivos en inglés

### 3.2 Estructura de Archivos

```
src/
├── ui/              # PRESENTATION - Vistas, Dialogs
├── controllers/     # APPLICATION - Orquestación
├── services/        # DOMAIN - Lógica de negocio
├── repository/      # DATA - Acceso a datos
├── models/          # DOMAIN - Entidades
├── database/        # INFRASTRUCTURE - DB config
└── utils/           # INFRASTRUCTURE - Helpers
```

### 3.3 Reglas de Oro

1. **SIEMPRE** usa Repository para acceso a datos
2. **NUNCA** hardcodees contraseñas o claves
3. **NUNCA** uses `except: pass` - siempre haz logging
4. **NUNCA** pongas lógica de negocio en UI - usa Controllers
5. **SIEMPRE** valida campos con whitelist
6. **NUNCA** instancies servicios dentro de widgets - inyecta
7. **SIEMPRE** usa type hints
8. **NUNCA** ignores errores - maneja y reporta al usuario

---

## 4. Testing

### 4.1 Ejecutar Tests

```bash
# Todos los tests
python3 -m pytest tests/ -v

# Con coverage
python3 -m pytest tests/ --cov=src --cov-report=html
```

### 4.2 Agregar Tests

- Ubicación: `tests/`
- Nombre: `test_nombre_modulo.py`
- Estructura:

```python
import sys
sys.path.insert(0, '.')

from unittest.mock import Mock
from src.services.module import Function

def test_function_behavior():
    """Test específico con descripción"""
    # Arrange
    mock = Mock()
    
    # Act
    result = Function(mock)
    
    # Assert
    assert result == expected
```

---

## 5. Documentación

### 5.1 Docstrings

Usa formato Google:

```python
def function(param1: str, param2: int) -> bool:
    """Descripción corta.
    
    Args:
        param1: Descripción del parámetro
        param2: Descripción del parámetro
    
    Returns:
        True si exitosa, False si no.
    
    Raises:
        ValueError: Si param1 está vacío.
    """
```

### 5.2 README

Si agregas una nueva característica, actualiza el README si es necesario.

---

## 6. Commits

### 6.1 Tipos de Commits

| Tipo | Descripción |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Bug fix |
| `refactor` | Refactorización (sin cambio de comportamiento) |
| `docs` | Documentación |
| `test` | Agregar/actualizar tests |
| `chore` | Mantenimiento general |

### 6.2 Mensajes

```
type(scope): mensaje corto

Mensaje más detallado si es necesario.
```

Ejemplos:
```
feat(auth): agregar validación de contraseña fuerte
fix(inventory): corregir cálculo de stock negativo
docs(readme): actualizar guía de instalación
```

---

## 7. Review Process

1. Un mantenedor revisará tu PR
2. Puede pedir cambios
3. Una vez aprobado, se mergea a `main`

---

## 8. Preguntas

Si tienes dudas, puedes abrir un issue con标签 "question".

¡Gracias por tu contribución! 🎉