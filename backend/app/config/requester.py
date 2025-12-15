from requests import Response, RequestException, get
from typing import List, Optional
import random
from .logger import get_logger

logger = get_logger(__name__)


def make_request(
    url: str,
    proxy_servers: Optional[List[str]] = None,
    user_agents: Optional[List[str]] = None,
    timeout: int = 60,
) -> Optional[Response]:
    """
    Make Get request to the specified URL and returns the response

    Args:
        url (str): The URL to make the request to

    Returns:
        Optional[Response]: The response object if the request was successful, None otherwise.
    """
    try:
        headers = {
            "User-Agent": random.choice(user_agents)
            if user_agents
            else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        if proxy_servers:
            proxy = random.choice(proxy_servers)
            proxies = {
                "http": proxy,
                "https": proxy,
            }
        else:
            proxies = None
        
        response = get(url, headers=headers, proxies=proxies, timeout=timeout)
        response.raise_for_status()  # Raise an error for bad responses
        return response
        
    except RequestException as err:
        logger.error("Request to %s failed: %s", url, str(err))
        return None
