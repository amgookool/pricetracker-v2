from typing import List, Optional
from uuid import UUID

from app.schemas.configs import ProxyTypes, UserAgentTypes
from app.schemas.users import UserRole
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ValidateAmazonProductASINResponseModel(BaseModel):
    # model_config = ConfigDict()

    name: str = Field(
        ...,
        title="Product Name",
        description="The name of the Amazon product.",
    )
    price: float = Field(
        ...,
        title="Product Price",
        description="The price of the Amazon product.",
    )
    image_url: str = Field(
        ...,
        title="Product Image URL",
        description="The URL of the product image.",
    )
    url: str = Field(
        ...,
        title="Product URL",
        description="The URL of the Amazon product page.",
    )
    