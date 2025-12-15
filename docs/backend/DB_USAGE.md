# SQLModel Database Utilities Usage Guide

This guide demonstrates how to use the database utility functions provided in `db.py` for working with SQLite and SQLModel.

## Table of Contents

- [Setup](#setup)
- [Defining Models](#defining-models)
- [Initializing the Database](#initializing-the-database)
- [Session Management](#session-management)
- [CRUD Operations](#crud-operations)
- [FastAPI Integration](#fastapi-integration)
- [Advanced Queries](#advanced-queries)

---

## Setup

The database utilities automatically use the `DATABASE` setting from your environment configuration (`.env` file):

```env
DATABASE=sqlite:///./database.db
```

---

## Defining Models

Define your SQLModel classes with table=True to create database tables:

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url: str
    current_price: float
    target_price: Optional[float] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PriceHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    price: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Initializing the Database

Create all tables on application startup:

```python
from app.config.db import create_db_and_tables

# In your main.py or app initialization
create_db_and_tables()
```

With FastAPI lifecycle events:

```python
from fastapi import FastAPI
from app.config.db import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("Database tables created successfully!")
```

---

## Session Management

### Option 1: Context Manager (Direct Usage)

Use `get_db_session()` for direct database operations outside of FastAPI routes:

```python
from app.config.db import get_db_session
from app.models import Product

# Automatic session management with rollback on errors
with get_db_session() as session:
    product = Product(name="Laptop", url="https://...", current_price=999.99)
    session.add(product)
    session.commit()
    print(f"Created product with ID: {product.id}")
```

### Option 2: Dependency Injection (FastAPI Routes)

Use `get_session()` with FastAPI's `Depends()`:

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.config.db import get_session

router = APIRouter()

@router.get("/products")
def list_products(session: Session = Depends(get_session)):
    # Session automatically managed by FastAPI
    products = session.exec(select(Product)).all()
    return products
```

---

## CRUD Operations

### Creating Records

```python
from app.config.db import get_db_session, create
from app.models import Product

# Using the create helper
with get_db_session() as session:
    new_product = Product(
        name="Wireless Mouse",
        url="https://example.com/mouse",
        current_price=29.99,
        target_price=25.00
    )
    created = create(session, new_product)
    print(f"Created product ID: {created.id}")

# Manual approach (without helper)
with get_db_session() as session:
    product = Product(name="Keyboard", url="https://...", current_price=59.99)
    session.add(product)
    session.commit()
    session.refresh(product)
```

### Reading Records

#### Get All Records (with pagination)

```python
from app.config.db import get_db_session, get_all
from app.models import Product

with get_db_session() as session:
    # Get first 50 products
    products = get_all(session, Product, skip=0, limit=50)
    
    # Get next 50 products (pagination)
    more_products = get_all(session, Product, skip=50, limit=50)
    
    for product in products:
        print(f"{product.name}: ${product.current_price}")
```

#### Get Record by ID

```python
from app.config.db import get_db_session, get_by_id
from app.models import Product

with get_db_session() as session:
    product = get_by_id(session, Product, record_id=1)
    
    if product:
        print(f"Found: {product.name}")
    else:
        print("Product not found")
```

#### Get Record by Field

```python
from app.config.db import get_db_session, get_by_field
from app.models import Product

with get_db_session() as session:
    # Find first product with specific name
    product = get_by_field(session, Product, "name", "Wireless Mouse")
    
    # Find first active product
    active_product = get_by_field(session, Product, "is_active", True)
```

#### Get All Records by Field

```python
from app.config.db import get_db_session, get_all_by_field
from app.models import Product

with get_db_session() as session:
    # Get all active products
    active_products = get_all_by_field(session, Product, "is_active", True)
    
    # Get all products at a specific price point
    budget_products = get_all_by_field(session, Product, "current_price", 29.99)
    
    print(f"Found {len(active_products)} active products")
```

### Updating Records

```python
from app.config.db import get_db_session, get_by_id, update
from app.models import Product

with get_db_session() as session:
    # Fetch the product
    product = get_by_id(session, Product, record_id=1)
    
    if product:
        # Update using the helper function
        updated = update(
            session, 
            product,
            current_price=24.99,
            is_active=True
        )
        print(f"Updated {updated.name} to ${updated.current_price}")

# Alternative: Update without commit (for batch operations)
with get_db_session() as session:
    product = get_by_id(session, Product, record_id=1)
    if product:
        update(session, product, commit=False, current_price=19.99)
        # Do more operations...
        session.commit()  # Commit all at once
```

### Deleting Records

```python
from app.config.db import get_db_session, get_by_id, delete
from app.models import Product

with get_db_session() as session:
    product = get_by_id(session, Product, record_id=1)
    
    if product:
        delete(session, product)
        print(f"Deleted product: {product.name}")

# Delete without immediate commit (for batch operations)
with get_db_session() as session:
    product = get_by_id(session, Product, record_id=2)
    if product:
        delete(session, product, commit=False)
        # Delete more records...
        session.commit()  # Commit all deletions at once
```

---

## FastAPI Integration

### Complete Route Example

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.config.db import get_session, get_all, get_by_id, create, update, delete
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[Product])
def list_products(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all products with pagination."""
    return get_all(session, Product, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    """Get a single product by ID."""
    product = get_by_id(session, Product, record_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=Product)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session)
):
    """Create a new product."""
    product = Product(**product_data.model_dump())
    return create(session, product)

@router.patch("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing product."""
    product = get_by_id(session, Product, record_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_data.model_dump(exclude_unset=True)
    return update(session, product, **update_data)

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    """Delete a product."""
    product = get_by_id(session, Product, record_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    delete(session, product)
    return {"message": "Product deleted successfully"}
```

---

## Advanced Queries

For complex queries beyond the basic CRUD helpers, use SQLModel's query API directly:

### Custom Filtering

```python
from sqlmodel import select
from app.config.db import get_db_session
from app.models import Product

with get_db_session() as session:
    # Multiple conditions
    statement = select(Product).where(
        Product.is_active == True,
        Product.current_price < 50.0
    )
    affordable_products = session.exec(statement).all()
    
    # OR conditions
    from sqlmodel import or_
    statement = select(Product).where(
        or_(
            Product.current_price < 20.0,
            Product.name.contains("Sale")
        )
    )
    bargains = session.exec(statement).all()
```

### Ordering and Limiting

```python
from sqlmodel import select
from app.config.db import get_db_session
from app.models import Product

with get_db_session() as session:
    # Order by price (ascending)
    statement = select(Product).order_by(Product.current_price)
    cheapest_first = session.exec(statement).all()
    
    # Order by price (descending) and limit
    statement = select(Product).order_by(Product.current_price.desc()).limit(10)
    most_expensive = session.exec(statement).all()
```

### Counting Records

```python
from sqlmodel import select, func
from app.config.db import get_db_session
from app.models import Product

with get_db_session() as session:
    # Count all products
    statement = select(func.count()).select_from(Product)
    total_count = session.exec(statement).one()
    
    # Count active products
    statement = select(func.count()).select_from(Product).where(Product.is_active == True)
    active_count = session.exec(statement).one()
```

### Joins and Relationships

```python
from sqlmodel import select
from app.config.db import get_db_session
from app.models import Product, PriceHistory

with get_db_session() as session:
    # Join products with their price history
    statement = select(Product, PriceHistory).join(
        PriceHistory, 
        Product.id == PriceHistory.product_id
    )
    results = session.exec(statement).all()
    
    for product, price_record in results:
        print(f"{product.name}: ${price_record.price} at {price_record.recorded_at}")
```

---

## Best Practices

1. **Always use context managers or dependency injection** - Never manage sessions manually
2. **Use transactions for multiple operations** - Set `commit=False` and commit once
3. **Handle exceptions gracefully** - The context manager automatically rolls back on errors
4. **Use type hints** - The generic helpers are fully typed for IDE support
5. **Index frequently queried fields** - Add `index=True` to SQLModel fields
6. **Validate data before creating records** - Use Pydantic schemas for input validation
7. **Use pagination** - Always use `skip` and `limit` for large result sets

---

## Error Handling Example

```python
from app.config.db import get_db_session, create
from app.models import Product
from sqlalchemy.exc import IntegrityError

with get_db_session() as session:
    try:
        product = Product(name="Test", url="https://...", current_price=99.99)
        create(session, product)
    except IntegrityError as e:
        print(f"Database constraint violation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Session automatically rolled back by context manager
```

---

## Summary

The database utilities in `db.py` provide:

- ✅ Automatic session lifecycle management
- ✅ FastAPI dependency injection support
- ✅ Type-safe generic CRUD operations
- ✅ Pagination support out of the box
- ✅ Flexible commit control for batch operations
- ✅ Clean, documented API for common database tasks

For anything beyond basic CRUD, you can always drop down to SQLModel's full query API while still using the session management helpers.
