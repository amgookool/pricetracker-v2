"""Database utilities for SQLModel-based SQLite interaction.

This module provides a centralized configuration and helper functions for
working with SQLModel and SQLite, including:
- Engine creation and lifecycle management
- Session context managers (both sync and dependency injection patterns)
- Table creation and schema initialization
- Generic CRUD operations for any SQLModel model

Usage:
    # Initialize tables on app startup
    create_db_and_tables()
    
    # Use in route handlers with dependency injection
    @app.get("/items")
    def get_items(session: Session = Depends(get_session)):
        items = get_all(session, Item)
        return items
    
    # Or use the context manager directly
    with get_db_session() as session:
        item = get_by_id(session, Item, item_id=1)
"""

from contextlib import contextmanager
from typing import Generator, Type, TypeVar, Optional, List, Any

from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.engine import Engine

from .settings import get_settings


# Type variable for generic SQLModel classes
T = TypeVar("T", bound=SQLModel)

# Load configuration
envConfig = get_settings()

# Global engine instance (created once per application lifecycle)
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Get or create the SQLite engine.
    
    The engine is created once and reused across the application lifecycle.
    Uses the DATABASE setting from the environment configuration.
    
    Returns:
        Engine: The SQLAlchemy engine instance.
    """
    global _engine
    if _engine is None:
        # Create engine with SQLite-specific options
        # echo=True would log all SQL statements (useful for debugging)
        _engine = create_engine(
            envConfig.DATABASE,
            echo=True,  # Set to True for SQL query logging
            connect_args={"check_same_thread": False}  # Needed for SQLite
        )
    return _engine


def create_db_and_tables() -> None:
    """Create all SQLModel tables in the database.
    
    This should be called once during application startup to ensure all
    tables defined in SQLModel classes are created. If tables already exist,
    this operation is idempotent (won't recreate them).
    
    Example:
        # In main.py or app startup
        @app.on_event("startup")
        def on_startup():
            create_db_and_tables()
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions.
    
    Automatically handles session lifecycle: creates, commits, and closes
    the session. If an exception occurs, the transaction is rolled back.
    
    Yields:
        Session: An active SQLModel session.
    
    Example:
        with get_db_session() as session:
            user = User(name="John")
            session.add(user)
            session.commit()
    """
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Generator[Session, None, None]:
    """Dependency injection helper for FastAPI route handlers.
    
    Use this with FastAPI's Depends() to automatically inject a database
    session into your route handlers. The session is automatically closed
    after the request completes.
    
    Yields:
        Session: An active SQLModel session.
    
    Example:
        from fastapi import Depends
        
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            users = session.exec(select(User)).all()
            return users
    """
    with get_db_session() as session:
        yield session


# ============================================================================
# Generic CRUD Operations
# ============================================================================


def get_all(session: Session, model: Type[T], skip: int = 0, limit: int = 100) -> List[T]:
    """Retrieve all records of a given model with pagination.
    
    Args:
        session: Active database session.
        model: The SQLModel class to query.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
    
    Returns:
        List of model instances.
    
    Example:
        with get_db_session() as session:
            products = get_all(session, Product, skip=0, limit=50)
    """
    statement = select(model).offset(skip).limit(limit)
    results = session.exec(statement)
    return results.all()


def get_by_id(session: Session, model: Type[T], record_id: Any) -> Optional[T]:
    """Retrieve a single record by its primary key ID.
    
    Args:
        session: Active database session.
        model: The SQLModel class to query.
        record_id: The primary key value to search for.
    
    Returns:
        The model instance if found, None otherwise.
    
    Example:
        with get_db_session() as session:
            product = get_by_id(session, Product, record_id=42)
    """
    return session.get(model, record_id)


def create(session: Session, instance: T, commit: bool = True) -> T:
    """Create a new record in the database.
    
    Args:
        session: Active database session.
        instance: The model instance to persist.
        commit: Whether to commit the transaction immediately.
    
    Returns:
        The created instance (with ID populated if auto-generated).
    
    Example:
        with get_db_session() as session:
            new_product = Product(name="Widget", price=9.99)
            created = create(session, new_product)
            print(created.id)  # Auto-generated ID
    """
    session.add(instance)
    if commit:
        session.commit()
        session.refresh(instance)
    return instance


def update(session: Session, instance: T, commit: bool = True, **kwargs) -> T:
    """Update an existing record with new field values.
    
    Args:
        session: Active database session.
        instance: The model instance to update.
        commit: Whether to commit the transaction immediately.
        **kwargs: Field names and new values to update.
    
    Returns:
        The updated instance.
    
    Example:
        with get_db_session() as session:
            product = get_by_id(session, Product, record_id=1)
            updated = update(session, product, price=12.99, name="New Name")
    """
    for key, value in kwargs.items():
        setattr(instance, key, value)
    session.add(instance)
    if commit:
        session.commit()
        session.refresh(instance)
    return instance


def delete(session: Session, instance: T, commit: bool = True) -> None:
    """Delete a record from the database.
    
    Args:
        session: Active database session.
        instance: The model instance to delete.
        commit: Whether to commit the transaction immediately.
    
    Example:
        with get_db_session() as session:
            product = get_by_id(session, Product, record_id=1)
            if product:
                delete(session, product)
    """
    session.delete(instance)
    if commit:
        session.commit()


def get_by_field(session: Session, model: Type[T], field_name: str, field_value: Any) -> Optional[T]:
    """Retrieve the first record matching a specific field value.
    
    Args:
        session: Active database session.
        model: The SQLModel class to query.
        field_name: The name of the field to filter by.
        field_value: The value to match.
    
    Returns:
        The first matching model instance, or None if not found.
    
    Example:
        with get_db_session() as session:
            user = get_by_field(session, User, "email", "user@example.com")
    """
    statement = select(model).where(getattr(model, field_name) == field_value)
    result = session.exec(statement)
    return result.first()


def get_all_by_field(session: Session, model: Type[T], field_name: str, field_value: Any) -> List[T]:
    """Retrieve all records matching a specific field value.
    
    Args:
        session: Active database session.
        model: The SQLModel class to query.
        field_name: The name of the field to filter by.
        field_value: The value to match.
    
    Returns:
        List of matching model instances.
    
    Example:
        with get_db_session() as session:
            active_users = get_all_by_field(session, User, "is_active", True)
    """
    statement = select(model).where(getattr(model, field_name) == field_value)
    results = session.exec(statement)
    return results.all()