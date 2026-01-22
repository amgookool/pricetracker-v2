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
    
    __tablename__="products"
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
        alias="scrapeLocation"
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
        alias="updatedAt"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the product was created",
        alias="createdAt"
    )


class ProductTrackingTable(SQLModel, table=True):
    
    __tablename__="product_tracking"
    
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
        foreign_key="products.id",
        alias="productId"
    )
    user_id: UUID = Field(
        ...,
        title="User Id",
        description="The id of the user who is tracking this product",
        foreign_key="users.id",
        alias="userId"
    )
    desired_price: Optional[float] = Field(
        None,
        title="Desired Price",
        description="The desired price set by the user for notifications",
        alias="desiredPrice"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the tracking entry was created",
        alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Updated At",
        description="Timestamp when the tracking entry was last updated",
        alias="updatedAt",
    )


class ProductHistoryTable(SQLModel, table=True):
    
    __tablename__="product_history"
    
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
        foreign_key="products.id",
        alias="productId"
    )
    tracking_id: UUID = Field(
        ...,
        title="Tracking Id",
        description="The Id of the product tracking entry from ProductTrackingTable",
        foreign_key="product_tracking.id",
        alias="trackingId"
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
        alias="recordedAt"
    )