import enum
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

# from .users import UsersTable


class ProductCategory(enum.Enum):
    ELECTRONICS = "ELECTRONICS"
    COMPUTERS = "COMPUTERS"
    ACCESSORIES = "ACCESSORIES"
    CLOTHING = "CLOTHING"
    HEALTHandBEAUTY = "HEALTH_AND_BEAUTY"
    AUTOMOTIVE = "AUTOMOTIVE"
    OFFICE = "OFFICE"
    HOME = "HOME"


class ProductScrapeLocation(enum.Enum):
    AMAZON = "AMAZON"
    EBAY = "EBAY"
    BESTBUY = "BESTBUY"


class ProductsTable(SQLModel, table=True):
    
    __tablename__="products_table"
    # Fields
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        title="Product Id",
        description="Unique identifier for the product",
    )
    name: str = Field(
        ...,
        title="Name of product",
        description="The name of the product scraped from webpage",
        index=True,
    )
    url: str = Field(
        ..., title="Product URL", description="The URL of the product page"
    )
    category: ProductCategory = Field(
        ...,
        title="Product Category",
        description="The category of the product",
        index=True,
    )
    scrape_location: ProductScrapeLocation = Field(
        ProductScrapeLocation.AMAZON,
        title="Scrape Location",
        description="The e-commerce platform where the product is listed",
        index=True,
    )
    price: Optional[float] = Field(
        None, title="Price", description="The current price of the product"
    )
    image: Optional[str] = Field(
        None, title="Image", description="The image URL of the product"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="The datetime at which the product was scraped",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the product was created",
    )


class ProductTrackingTable(SQLModel, table=True):
    
    __tablename__="product_tracking_table"
    
    # Fields
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        title="Tracking Id",
        description="Unique identifier for the product tracking entry",
    )
    product_id: UUID = Field(
        ...,
        title="Product Id",
        description="The Id of the product being tracked from ProductsTable",
        foreign_key="products_table.id",
    )
    user_id: UUID = Field(
        ...,
        title="User Id",
        description="The id of the user who is tracking this product",
        foreign_key="users_table.id",
    )
    desired_price: Optional[float] = Field(
        None,
        title="Desired Price",
        description="The desired price set by the user for notifications",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the tracking entry was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Updated At",
        description="Timestamp when the tracking entry was last updated",
    )


class ProductHistoryTable(SQLModel, table=True):
    
    __tablename__="product_history_table"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        title="History Id",
        description="Unique identifier for the product history entry",
    )
    product_id: UUID = Field(
        ...,
        title="Product Id",
        description="The Id of the product from ProductsTable",
        foreign_key="products_table.id",
    )
    tracking_id: UUID = Field(
        ...,
        title="Tracking Id",
        description="The Id of the product tracking entry from ProductTrackingTable",
        foreign_key="product_tracking_table.id",
    )
    price: float = Field(
        ...,
        title="Price",
        description="The price of the product at the time of recording",
    )
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Recorded At",
        description="Timestamp when the price was recorded",
    )