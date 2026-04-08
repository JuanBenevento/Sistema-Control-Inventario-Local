"""Repository para proveedores."""
from sqlalchemy.orm import Session
from src.models.entities import Supplier, Product


# Whitelist de campos permitidos para actualización
ALLOWED_UPDATE_FIELDS = {'name', 'contact_name', 'phone', 'email', 'address', 'notes', 'is_active'}


class SupplierRepository:
    """Repository para operaciones de proveedores."""

    @staticmethod
    def get_all(db: Session, include_inactive: bool = False) -> list:
        """Obtiene todos los proveedores."""
        query = db.query(Supplier)
        if not include_inactive:
            query = query.filter(Supplier.is_active == True)
        return query.order_by(Supplier.name).all()

    @staticmethod
    def get_by_id(db: Session, supplier_id: int) -> Supplier:
        """Obtiene un proveedor por ID."""
        return db.query(Supplier).filter(Supplier.id == supplier_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Supplier:
        """Obtiene un proveedor por nombre."""
        return db.query(Supplier).filter(
            Supplier.name == name,
            Supplier.is_active == True
        ).first()

    @staticmethod
    def search(db: Session, term: str) -> list:
        """Busca proveedores por nombre o contacto."""
        term = f"%{term}%"
        return db.query(Supplier).filter(
            Supplier.is_active == True,
            (Supplier.name.ilike(term) | Supplier.contact_name.ilike(term))
        ).order_by(Supplier.name).all()

    @staticmethod
    def create(db: Session, name: str, contact_name: str = None,
               phone: str = None, email: str = None,
               address: str = None, notes: str = None) -> Supplier:
        """Crea un nuevo proveedor."""
        supplier = Supplier(
            name=name,
            contact_name=contact_name,
            phone=phone,
            email=email,
            address=address,
            notes=notes,
            is_active=True
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def update(db: Session, supplier_id: int, **fields) -> Supplier:
        """Actualiza un proveedor. Solo campos en whitelist."""
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return None
        
        # Filtrar solo campos permitidos (whitelist)
        allowed = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
        
        for key, value in allowed.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)
        
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def delete(db: Session, supplier_id: int, soft: bool = True) -> bool:
        """
        Elimina un proveedor.
        
        Si soft=True (default): borrado lógico
        Si soft=False: eliminación física
        """
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return False
        
        if soft:
            supplier.is_active = False
            db.commit()
        else:
            db.delete(supplier)
            db.commit()
        
        return True

    @staticmethod
    def has_products(db: Session, supplier_id: int) -> bool:
        """Verifica si un proveedor tiene productos asociados."""
        return db.query(Product).filter(
            Product.supplier_id == supplier_id
        ).count() > 0