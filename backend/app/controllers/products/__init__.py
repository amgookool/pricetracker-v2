from datetime import timedelta
from typing import Annotated, List
import re
from urllib.parse import quote

from app.config.db import Session, get_session
from app.config.logger import get_logger
from app.config.settings import get_settings
from app.controllers.auth.models import UserResponseModel
from app.middleware.auth import get_access_user
from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.responses import JSONResponse




from .models import ValidateAmazonProductASINResponseModel

from .service import fetch_amazon_product_data

# FastAPI Router
router = APIRouter()

# Logger
logger = get_logger(__name__)

# Environment Vars
SETTINGS = get_settings()


@router.get(
    "/amazon/validate/{product_asin}",
    summary="Validate Amazon Product ASIN",
    description="Validate if the provided ASIN corresponds to a valid Amazon product.",
    response_model=ValidateAmazonProductASINResponseModel,
)
async def validate_amazon_product_asin(
    product_asin: Annotated[
        str,
        Path(
            title="Product ASIN",
            description="The ASIN of the Amazon product to validate.",
        ),
    ],
    active_user: Annotated[UserResponseModel, Depends(get_access_user)],
    session: Annotated[Session, Depends(get_session)],
):
    try:
        # sanitize ASIN: remove non-alphanumeric characters (including invisible Unicode marks)
        clean_asin = re.sub(r'[^A-Za-z0-9]', '', product_asin or '')
        if not clean_asin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ASIN provided.",
            )

        # build URL using cleaned ASIN (quote for safety)
        prod_url = f"https://www.amazon.com/dp/{quote(clean_asin, safe='')}"

        await fetch_amazon_product_data(product_url=prod_url, db_session=session)

        response_model = ValidateAmazonProductASINResponseModel(
            name="Sample Product",
            price=19.99,
            image_url="https://example.com/sample-product.jpg",
            url=f"https://www.amazon.com/dp/{clean_asin}",
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_model.model_dump(mode="json", by_alias=True),
        )
    except HTTPException as http_e:
        logger.error("HTTP error while validating ASIN: %s", http_e.detail)
        raise http_e
    except Exception as general_e:
        logger.exception("Error validating ASIN: %s", general_e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while validating the ASIN.",
        )
