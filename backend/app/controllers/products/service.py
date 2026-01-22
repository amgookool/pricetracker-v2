# from app.schemas.products import (
#     ProductHistoryTable,
#     ProductsTable,
#     ProductTrackingTable,
#     ProductCategory,
#     ProductScrapeLocation,
# )
from app.config.db import (
    get_db_session,
    Session,
    get_all,
    get_by_id,
    get_by_field,
    get_all_by_field,
    select,
)
from sqlmodel import or_
from app.config.logger import get_logger

from app.web.amazon import AmazonPageParser

from app.schemas.configs import (
    ProxyTypes,
    ProxiesTable,
    UserAgentsTable,
    UserAgentTypes,
)

# from app.schemas.configs import ProxiesTable

from typing import List, Optional
from app.config.requester import make_request, generate_http_proxy_address

# Initialize logger
logger = get_logger(__name__)


async def fetch_amazon_product_data(
    product_url: str,
    db_session: Session,
):
    """Validate if the provided ASIN corresponds to a valid Amazon product."""
    try:
        # Get HTTP proxies
        sql_proxy_query = select(ProxiesTable).where(
            or_(
                ProxiesTable.proxy_type == ProxyTypes.HTTP,
                ProxiesTable.proxy_type == ProxyTypes.HTTPS,
            )
        )
        proxy_records = db_session.exec(sql_proxy_query).all()

        request_proxies = [
            generate_http_proxy_address(
                ip=prox.ip_address,
                port=prox.port,
                username=prox.username if prox.username else None,
                password=prox.password if prox.password else None,
            )
            for prox in proxy_records
        ]

        # Get User Agents
        sql_ua_query = select(UserAgentsTable).where(
            UserAgentsTable.type == UserAgentTypes.DESKTOP
        )
        ua_records = db_session.exec(sql_ua_query).all()
        
        request_agents: List[str] = [ua.user_agent for ua in ua_records]
        
        
        found_all_data: bool = False
        scrape_attempts: int = 0
        max_scrape_attempts: int = 5
        
        data = {
            "title": None,
            "price": None,
            "image": None,
            "seller": None,
            "coupon": None,
        }
        
        while not found_all_data and scrape_attempts < max_scrape_attempts:
            scrape_attempts += 1
            page_content = await make_request(
                "https://www.amazon.com/Apple-iPad-Pro-13-inch-Landscape/dp/B0FWD64873/",
                proxy_servers=request_proxies,
                user_agents=request_agents,
            )
            parser = AmazonPageParser(page_content.content)
            
            
            product_title = parser.parse_product_name()
            product_price = parser.parse_product_price()
            
            if product_title or parser.name:
                data["title"] = product_title if product_title else parser.name
            if product_price or parser.price:
                data["price"] = product_price if product_price else parser.price
                
            # if parser.image_url:
            #     data["image"] = parser.image_url
                
            # if parser.seller_name:
            #     data["seller"] = parser.seller_name
            
            if data["title"] and data["price"]:
                found_all_data = True
                
        print(f"Scrape data: {data}")
            
            
        # product_image = parser.parse_product_image()
        # product_seller = parser.parse_product_seller()
        # product_coupon = parser.parse_product_coupon()
        
        # print(f"Product Title: {product_title}")
        # print(f"Product Price: {product_price}")
        # print(f"Product Image: {product_image}")
        # print(f"Product Seller: {product_seller}")
        # print(f"Product Coupon: {product_coupon}")

        is_valid = True  # Replace with actual validation result
        return is_valid
    except Exception as e:
        logger.exception("Error validating Amazon product ASIN: %s", e)
        raise e
