from dataclasses import dataclass
from app.config.logger import get_logger
import re
from typing import Optional, Tuple, Dict, TypedDict, List, Literal

from bs4 import BeautifulSoup


@dataclass
class AmazonProductSeller:
    """
    TypedDict for Amazon product seller information.

    ships_from: The location from which the product is shipped. Can be None if not available which indicates that the product is sold and shipped by the same entity as the sold_by.

    sold_by: The seller of the product. Can be None if not available which indicates that the product is sold and shipped by Amazon directly.
    """

    ships_from: Optional[str]
    sold_by: Optional[str]


@dataclass
class AmazonProductCoupon:
    """
    TypedDict for Amazon product coupon information.

    type: The type of coupon, either 'fixed' for a fixed amount discount or 'percentage' for a percentage-based discount.

    amount: The amount of the discount. For 'fixed' type, this is a float representing the dollar amount. For 'percentage' type, this is a float representing the percentage.
    """

    type: Literal["fixed", "percentage"]  # 'fixed' or 'percentage'
    amount: float


class AmazonPageParser:
    def __init__(self, html_content: str):
        # HTML content of the Amazon product page
        self.html_content = html_content
        # Data keys to extract
        self.price: Optional[float] = None
        self.name: Optional[str] = None
        self.image_url: Optional[str] = None
        self.seller: Optional[AmazonProductSeller] = None
        self.coupon: Optional[AmazonProductCoupon] = None
        # Class Logger
        self.logger = get_logger(self.__class__.__name__)
        # BeautifulSoup Parser
        # html.parser, lxml, html5lib
        self.soup = BeautifulSoup(self.html_content, "html.parser")

    def parse_product_name(self) -> Optional[str]:
        """Extract the product name from the Amazon product page."""

        def method1():
            title_element = self.soup.find(id="ProductTitle")
            if title_element:
                return title_element.get_text(strip=True)
            return None

        def method2():
            title_feature_element = self.soup.find(id="title_feature_div")
            if not title_feature_element:
                return None
            title_element = title_feature_element.find(id="productTitle")
            if title_element:
                return title_element.get_text(strip=True)
            return None

        self.logger.info("Attempting to parse product name using available methods.")
        try:
            name = method1()
            if name:
                self.name = name
                return name
        except Exception as e:
            self.logger.warning("Method 1 failed to parse product name: %s", e)

        try:
            name = method2()
            if name:
                self.name = name
                return name
        except Exception as e:
            self.logger.warning("Method 2 failed to parse product name: %s", e)

        self.logger.warning("Product name not found in the HTML content.")
        return None

    def parse_product_price(self) -> Optional[float]:
        """Extract the product price from the Amazon product page."""

        def method1():
            center_col_element = self.soup.find(id="centerCol")
            if not center_col_element:
                self.logger.warning(
                    "Center column element not found from method 1",
                )
                return None

            apex_desktop_div = center_col_element.find("div", id="apex_desktop")
            if not apex_desktop_div:
                self.logger.warning(
                    "Apex desktop div not found from method 1",
                )
                return None

            apex_desktop_accordion = apex_desktop_div.find(
                "div", id="apex_desktop_newAccordionRow"
            )
            if not apex_desktop_accordion:
                self.logger.warning(
                    "Apex desktop accordion not found from method 1",
                )
                return None
            core_price_display_element = apex_desktop_accordion.find(
                "div", id="corePriceDisplay_desktop_feature_div"
            )
            if not core_price_display_element:
                self.logger.warning(
                    "Core price display element not found from method 1",
                )
                return None

            corePrice_text = core_price_display_element.get_text(strip=False).split()
            if len(corePrice_text) > 0:
                price_text = corePrice_text[0]
                price_match = re.search(r"[\d,.]+", price_text)
                if price_match:
                    price_str = price_match.group().replace(",", "")
                    try:
                        return float(price_str)
                    except ValueError:
                        self.logger.error(
                            "Failed to convert price to float in method 1",
                        )
                        return None
            self.logger.warning(
                "Product price not found from method 1",
            )
            return None

        def method2():
            buybox_element = self.soup.find(id="buybox")
            if not buybox_element:
                self.logger.warning(
                    "Buybox element not found from method 2",
                )
                return None
            buybox_accordion_feature_element = buybox_element.find(
                "div", id="accordionRows_feature_div"
            )
            if not buybox_accordion_feature_element:
                self.logger.warning(
                    "Buybox accordion element not found from method 2",
                )
                return None

            buybox_accordion_element = buybox_accordion_feature_element.find(
                "div", id="buyBoxAccordion"
            )
            if not buybox_accordion_element:
                self.logger.warning(
                    "Buybox accordion element not found from method 2",
                )
                return None
            
            accordian_row_element = buybox_accordion_element.find_all("div")[0]
            if not accordian_row_element:
                self.logger.warning(
                    "Accordion row element not found from method 2",
                )
                return None
            
            core_price_feature_div = accordian_row_element.find(
                "div", id="corePrice_feature_div"
            )
            if not core_price_feature_div:
                self.logger.warning(
                    "Core price feature div not found from method 2",
                )
                return None
            
            corePrice_text = core_price_feature_div.get_text(strip=True).split('$').pop()

            price_match = re.search(r"[\d,.]+", corePrice_text)
            if price_match:
                price_str = price_match.group().replace(",", "")
                try:
                    return float(price_str)
                except ValueError:
                    self.logger.error(
                        "Failed to convert price to float in method 1",
                    )
                    return None
                
            self.logger.warning(
                "Product price not found from method 2",
            )
            return None
        
        def method3():
            coreprice_element = self.soup.find("div",
                id="corePriceDisplay_desktop_feature_div"
            )
            if not coreprice_element:
                self.logger.warning(
                    "Core price element not found from method 3",
                )
                return None
            price_text = coreprice_element.get_text(strip=True)
            print(f"Core Price Text: {price_text}")
        
        self.logger.info("Attempting to parse product price using available methods.")
        try:
            price = method1()
            if price is not None:
                self.price = price
                return price
        except Exception as e:
            self.logger.warning("Method 1 failed to parse product price: %s", e)
            
        try:
            price = method2()
            if price is not None:
                self.price = price
                return price
        except Exception as e:
            self.logger.warning("Method 2 failed to parse product price: %s", e)

        try:
            price = method3()
            if price is not None:
                self.price = price
                return price
        except Exception as e:
            self.logger.warning("Method 3 failed to parse product price: %s", e)
        
        self.logger.warning("Product price not found in the HTML content.")
        return None

    def parse_product_image(self) -> Optional[str]:
        """Extract the product image URL from the Amazon product page."""
        
        def method1():
            pass
        
        def method2():
            pass
        
        self.logger.info("Attempting to parse product image URL using available methods.")
        try:
            image_url = method1()
            if image_url:
                self.image_url = image_url
                return image_url
        except Exception as e:
            self.logger.warning("Method 1 failed to parse product image URL: %s", e)
            
        try:
            image_url = method2()
            if image_url:
                self.image_url = image_url
                return image_url
        except Exception as e:
            self.logger.warning("Method 2 failed to parse product image URL: %s", e)
        self.logger.warning("Product image URL not found in the HTML content.")
        return None
        

    # def parse_product_seller(self) -> Optional[Dict[str, str]]:
    #     """Extract the product seller from the Amazon product page."""
    #     container_element = self.soup.find(id="desktop_qualifiedBuyBox")
    #     if not container_element:
    #         self.logger.warning("Container element not found in the HTML content.")
    #         return None
    #     seller_container = container_element.find(id="offer-display-features")
    #     if not seller_container:
    #         self.logger.warning("Seller container not found in the HTML content.")
    #         return None
    #     ships_from_element = seller_container.find(
    #         id="fulfillerInfoFeature_feature_div"
    #     )

    #     sold_by_element = seller_container.find(id="merchantInfoFeature_feature_div")
    #     if not ships_from_element:
    #         self.logger.warning("Ships from element not found in the HTML content.")

    #     if ships_from_element:
    #         ships_from_data = ships_from_element.find(
    #             "span", class_="a-size-small offer-display-feature-text-message"
    #         ).get_text(strip=True)

    #     if not sold_by_element:
    #         self.logger.warning("Sold by element not found in the HTML content.")

    #     if sold_by_element:
    #         sold_by_data = sold_by_element.find(
    #             "span", class_="a-size-small offer-display-feature-text-message"
    #         ).get_text(strip=True)

    #     if not ships_from_element and not sold_by_element:
    #         self.logger.warning(
    #             "Neither ships from nor sold by elements found in the HTML content."
    #         )
    #         return None

    #     return {
    #         "ships_from": ships_from_data if ships_from_data else None,
    #         "sold_by": sold_by_data if sold_by_data else None,
    #     }

    # def parse_product_image(self)-> Optional[str]:
    #     """Extract the product image URL from the Amazon product page."""
    #     image_container = self.soup.find(id="imgTagWrapperId")
    #     if not image_container:
    #         self.logger.warning(
    #             "Product image container not found %s",
    #             f"for {self.user_product_name}" or "",
    #         )
    #         return None
    #     img_tag = image_container.find("img")
    #     if not img_tag or not img_tag.has_attr("src"):
    #         self.logger.warning(
    #             "Product image tag not found %s",
    #             f"for {self.user_product_name}" or "",
    #         )
    #         return None
    #     return img_tag.get("src")

    # def check_coupon_type(self, text: str) -> Optional[Tuple[str, float]]:
    #     """
    #     Helper function to check the type of coupon on the product.

    #     There can be two (2) types of coupons:
    #     1. Fixed amount coupon (e.g., $10 off)
    #     2. Percentage-based coupon (e.g., 15% off)
    #     """
    #     # Check for fixed amount coupon
    #     fixed_amount_match = re.search(r"\$(\d+(?:\.\d{1,2})?)", text)
    #     if fixed_amount_match:
    #         amount = float(fixed_amount_match.group(1))
    #         return ("fixed", amount)

    #     # Check for percentage-based coupon
    #     percent_match = re.search(r"(\d+(?:\.\d{1,2})?)%", text)
    #     if percent_match:
    #         percent = float(percent_match.group(1))
    #         return ("percentage", percent)

    #     return None

    # def parse_product_coupon(self) -> Optional[Dict[str, float|str|None]]:
    #     """Extract the product coupon information from the Amazon product page."""
    #     coupon_element = self.soup.find(id="promoPriceBlockMessage_feature_div")
    #     if not coupon_element:
    #         self.logger.info(
    #             "No coupon found %s", f"for {self.user_product_name}" or ""
    #         )
    #         return None

    #     coupon_message_element = coupon_element.find(
    #         "span", class_="a-color-success couponLabelText"
    #     )
    #     if not coupon_message_element:
    #         coupon_message = coupon_element.get_text(strip=True)
    #     else:
    #         coupon_message = coupon_message_element.get_text(strip=True)

    #     parsed_discount = self.check_coupon_type(coupon_message)

    #     type, discount = parsed_discount if parsed_discount else None

    #     if not type and not discount:
    #         self.logger.warning(
    #             "Unable to determine coupon type %s", f"for {self.user_product_name}" or ""
    #         )
    #         return None

    #     return {
    #         "type": type,
    #         "amount": discount,
    #     }
