"""Repository para categorías."""
from sqlalchemy.orm import Session
from src.models.entities import Category, Product


# Whitelist de campos permitidos para actualización
ALLOWED_UPDATE_FIELDS = {'name', 'description', 'parent_id', 'is_active'}


class CategoryRepository:
    """Repository para operaciones de categorías."""

    @staticmethod
    def get_all(db: Session, include_inactive: bool = False) -> list:
        """Obtiene todas las categorías activas."""
        query = db.query(Category)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        return query.order_by(Category.name).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Category:
        """Obtiene una categoría por ID."""
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Category:
        """Obtiene una categoría por nombre."""
        return db.query(Category).filter(
            Category.name == name,
            Category.is_active == True
        ).first()

    @staticmethod
    def get_root_categories(db: Session) -> list:
        """Obtiene categorías de nivel superior (sin padre)."""
        return db.query(Category).filter(
            Category.parent_id == None,
            Category.is_active == True
        ).order_by(Category.name).all()

    @staticmethod
    def get_children(db: Session, parent_id: int) -> list:
        """Obtiene subcategorías de una categoría."""
        return db.query(Category).filter(
            Category.parent_id == parent_id,
            Category.is_active == True
        ).order_by(Category.name).all()

    @staticmethod
    def create(db: Session, name: str, description: str = None,
               parent_id: int = None) -> Category:
        """Crea una nueva categoría."""
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id,
            is_active=True
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def update(db: Session, category_id: int, **fields) -> Category:
        """Actualiza una categoría. Solo campos en whitelist."""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        
        # Filtrar solo campos permitidos (whitelist)
        allowed = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
        
        for key, value in allowed.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category_id: int, soft: bool = True) -> bool:
        """Elimina una categoría."""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False
        
        if soft:
            category.is_active = False
            db.commit()
        else:
            db.delete(category)
            db.commit()
        
        return True

    @staticmethod
    def has_children(db: Session, category_id: int) -> bool:
        """Verifica si una categoría tiene subcategorías."""
        return db.query(Category).filter(
            Category.parent_id == category_id,
            Category.is_active == True
        ).count() > 0

    @staticmethod
    def has_products(db: Session, category_id: int) -> bool:
        """Verifica si una categoría tiene productos asociados."""
        return db.query(Product).filter(
            Product.category_id == category_id
        ).count() > 0

    @staticmethod
    def get_or_create_default(db: Session) -> Category:
        """Obtiene o crea la categoría 'Sin Categoría'."""
        default = db.query(Category).filter(
            Category.name == "Sin Categoría",
            Category.parent_id == None
        ).first()
        
        if not default:
            default = Category(
                name="Sin Categoría",
                description="Categoría por defecto para productos sin clasificar",
                is_active=True
            )
            db.add(default)
            db.commit()
            db.refresh(default)
        
        return default