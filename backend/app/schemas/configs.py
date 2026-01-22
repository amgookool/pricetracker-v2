import enum
from datetime import datetime, timezone
from typing import Optional, TypedDict, List, Literal
from app.config.settings import get_settings

# from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


# Environment settings
SETTINGS = get_settings()


########################### USER AGENTS TABLE & Data Setup ###########################
class ProxyServerEntry(TypedDict):
    name: str
    ip: str
    port: int
    type: Literal["http", "https", "socks4", "socks5"]
    username: Optional[str]
    password: Optional[str]
    
PROXY_SERVERS: List[ProxyServerEntry] = [
    {
        "name": "Gluetun HTTP Proxy Server",
        "ip": "127.0.0.1",
        "port": 8888,
        "username": SETTINGS.GLUETUN_USER,
        "password": SETTINGS.GLUETUN_PASSWORD,
        "type": "http",
    },
    {
        "name": "Gluetun SOCKS5 Proxy Server",
        "ip": "127.0.0.1",
        "port": 8388,
        "type": "socks5",
        "username": None,
        "password": None,
    }
]


class ProxyTypes(enum.Enum):
    """Enumeration for different types of proxies."""

    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"



class ProxiesTable(SQLModel, table=True):
    __tablename__ = "proxies"

    # Fields
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        title="Proxy Id",
        description="Unique identifier for the proxy",
    )
    ip_address: str = Field(
        ...,
        title="IP Address",
        description="The IP address of the proxy server",
        index=True,
        alias="ipAddress",
    )
    port: int = Field(
        ...,
        title="Port",
        description="The port number of the proxy server",
    )
    username: Optional[str] = Field(
        None,
        title="Username",
        description="The username for proxy authentication, if required",
    )
    password: Optional[str] = Field(
        None,
        title="Password",
        description="The password for proxy authentication, if required",
    )
    proxy_type: ProxyTypes = Field(
        ...,
        title="Proxy Type",
        description="The type of the proxy server",
        alias="proxyType",
        index=True,
    )
    proxy_name: str = Field(
        ...,
        title="Proxy Name",
        description="A user-defined name for the proxy",
        unique=True,
        alias="proxyName",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the proxy was added",
        alias="createdAt",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Updated At",
        description="Timestamp when the proxy was last updated",
        alias="updatedAt",
    )


########################### USER AGENTS TABLE & Data Setup ###########################
class DesktopUAEntry(TypedDict):
    agent: str
    browser: str
    os: str


DESKTOP_UA: List[DesktopUAEntry] = [
    # {
    #     "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    #     "browser": "Chrome 134.0.0",
    #     "os": "Windows 10/11",
    # },
    # {
    #     "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.3124.85",
    #     "browser": "Edge 134.0.3124",
    #     "os": "Windows 10/11",
    # },
    # {
    #     "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    #     "browser": "Firefox 136.0",
    #     "os": "Windows 10/11",
    # },
    {
        "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "browser": "Chrome 134.0.0",
        "os": "Mac OS X 10.15.7",
    },
    # {
    #     "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15",
    #     "browser": "Safari 18.3",
    #     "os": "Mac OS X 14.7.4",
    # },
    # {
    #     "agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:136.0) Gecko/20100101 Firefox/136.0",
    #     "browser": "Firefox 136.0",
    #     "os": "Ubuntu Linux",
    # },
    # {
    #     "agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
    #     "browser": "Firefox 136.0",
    #     "os": "Fedora Linux",
    # },
]


class UserAgentTypes(enum.Enum):
    """Enumeration for different types of user agents."""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    BOT = "bot"


class UserAgentsTable(SQLModel, table=True):
    __tablename__ = "user_agents"
    # Fields
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        title="User Agent Id",
        description="Unique identifier for the user agent",
    )
    user_agent: str = Field(
        ...,
        title="User Agent",
        description="The user agent string",
        unique=True,
        alias="userAgent",
    )
    type: UserAgentTypes = Field(
        ...,
        title="User Agent Type",
        description="The type/category of the user agent",
        index=True,
    )
    agent_browser: str = Field(
        ...,
        title="Agent Browser",
        description="The browser associated with the user agent",
        alias="agentBrowser",
        index=True,
    )
    agent_os: str = Field(
        ...,
        title="Agent Operating System",
        description="The operating system associated with the user agent",
        alias="agentOS",
        index=True,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        title="Created At",
        description="Timestamp when the user agent was added",
        alias="createdAt",
    )
