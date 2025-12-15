from app.config.logger import get_logger
import re
from typing import Optional, Tuple, Dict

from bs4 import BeautifulSoup


class AmazonPageParser:
    def __init__(self, html_content: str, user_product_name: Optional[str] = None):
        self.soup = BeautifulSoup(html_content, "lxml")
        self.logger = get_logger(self.__class__.__name__)
        self.user_product_name = user_product_name

    def parse_product_title(self) -> Optional[str]:
        """Extract the product title from the Amazon product page."""
        title_tag = self.soup.find(id="title_feature_div")
        if title_tag:
            title = title_tag.get_text(strip=True)
            return title
        self.logger.warning(
            "Product title not found %s", f"for {self.user_product_name}" or ""
        )
        return None

    def parse_product_price(self) -> Optional[float]:
        """Extract the product price from the Amazon product page."""
        price_element = self.soup.find("div", id="corePrice_feature_div")
        if not price_element:
            self.logger.warning(
                "Product price not found %s", f"for {self.user_product_name}" or ""
            )
            return None
        price_text_tag = price_element.find("span", class_="a-offscreen")
        if not price_text_tag:
            self.logger.warning(
                "Product price not found %s", f"for {self.user_product_name}" or ""
            )
            return None

        price_text = price_text_tag.get_text(strip=True)
        price_match = re.search(r"[\d,.]+", price_text)
        if price_match:
            price_str = price_match.group().replace(",", "")
            try:
                return float(price_str)
            except ValueError:
                self.logger.error(
                    "Failed to convert price to float %s",
                    f"for {self.user_product_name}" or "",
                )
                return None
        self.logger.warning(
            "Product price not found %s", f"for {self.user_product_name}" or ""
        )
        return None

    def parse_product_seller(self) -> Optional[Dict[str, str]]:
        """Extract the product seller from the Amazon product page."""
        container_element = self.soup.find(id="desktop_qualifiedBuyBox")
        if not container_element:
            self.logger.warning("Container element not found in the HTML content.")
            return None
        seller_container = container_element.find(id="offer-display-features")
        if not seller_container:
            self.logger.warning("Seller container not found in the HTML content.")
            return None
        ships_from_element = seller_container.find(
            id="fulfillerInfoFeature_feature_div"
        )

        sold_by_element = seller_container.find(id="merchantInfoFeature_feature_div")
        if not ships_from_element:
            self.logger.warning("Ships from element not found in the HTML content.")

        if ships_from_element:
            ships_from_data = ships_from_element.find(
                "span", class_="a-size-small offer-display-feature-text-message"
            ).get_text(strip=True)

        if not sold_by_element:
            self.logger.warning("Sold by element not found in the HTML content.")

        if sold_by_element:
            sold_by_data = sold_by_element.find(
                "span", class_="a-size-small offer-display-feature-text-message"
            ).get_text(strip=True)

        if not ships_from_element and not sold_by_element:
            self.logger.warning(
                "Neither ships from nor sold by elements found in the HTML content."
            )
            return None

        return {
            "ships_from": ships_from_data if ships_from_data else None,
            "sold_by": sold_by_data if sold_by_data else None,
        }

    def parse_product_image(self)-> Optional[str]:
        """Extract the product image URL from the Amazon product page."""
        image_container = self.soup.find(id="imgTagWrapperId")
        if not image_container:
            self.logger.warning(
                "Product image container not found %s",
                f"for {self.user_product_name}" or "",
            )
            return None
        img_tag = image_container.find("img")
        if not img_tag or not img_tag.has_attr("src"):
            self.logger.warning(
                "Product image tag not found %s",
                f"for {self.user_product_name}" or "",
            )
            return None
        return img_tag.get("src")
    
    def check_coupon_type(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Helper function to check the type of coupon on the product.
        
        There can be two (2) types of coupons:
        1. Fixed amount coupon (e.g., $10 off)
        2. Percentage-based coupon (e.g., 15% off)
        """
        # Check for fixed amount coupon
        fixed_amount_match = re.search(r"\$(\d+(?:\.\d{1,2})?)", text)
        if fixed_amount_match:
            amount = float(fixed_amount_match.group(1))
            return ("fixed", amount)
        
        # Check for percentage-based coupon
        percent_match = re.search(r"(\d+(?:\.\d{1,2})?)%", text)
        if percent_match:
            percent = float(percent_match.group(1))
            return ("percentage", percent)
        
        return None
    
    def parse_product_coupon(self) -> Optional[Dict[str, float|str|None]]:
        """Extract the product coupon information from the Amazon product page."""
        coupon_element = self.soup.find(id="promoPriceBlockMessage_feature_div")
        if not coupon_element:
            self.logger.info(
                "No coupon found %s", f"for {self.user_product_name}" or ""
            )
            return None
        
        coupon_message_element = coupon_element.find(
            "span", class_="a-color-success couponLabelText"
        )
        if not coupon_message_element:
            coupon_message = coupon_element.get_text(strip=True)
        else:
            coupon_message = coupon_message_element.get_text(strip=True)
            
            
        parsed_discount = self.check_coupon_type(coupon_message)
        
        type, discount = parsed_discount if parsed_discount else None
        
        if not type and not discount:
            self.logger.warning(
                "Unable to determine coupon type %s", f"for {self.user_product_name}" or ""
            )
            return None
        
        return {
            "type": type,
            "amount": discount,
        }
        