"""Database schemas/models for the application.

Import all SQLModel table classes here to ensure they are registered
with SQLModel.metadata before create_db_and_tables() is called.
"""

from .users import UsersTable
from .products import ProductsTable, ProductTrackingTable, ProductHistoryTable
from .schedules import SchedulesTable

__all__ = [
    "UsersTable",
    "ProductsTable",
    "SchedulesTable",
    "ProductTrackingTable",
    "ProductHistoryTable",
]
