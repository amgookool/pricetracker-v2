from typing import List, Optional
from uuid import UUID

from app.schemas.configs import ProxyTypes, UserAgentTypes
from app.schemas.users import UserRole
from pydantic import BaseModel, ConfigDict, EmailStr, Field

####################### Proxy Models #######################


class FetchProxiesResponseModel(BaseModel):
    """The FetchProxiesResponseModel defines the structure of the response for fetching proxy configurations."""

    model_config = ConfigDict(
        title="Fetch Proxies Response Model",
        description="Model representing the response for fetching proxy configurations",
        populate_by_name=True,
    )

    # Fields
    id: UUID = Field(
        ...,
        title="Proxy Id",
        description="Unique identifier for the proxy",
    )
    ip_address: str = Field(
        ...,
        title="IP Address",
        description="The IP address of the proxy server",
        alias="ipAddress",
    )
    port: int = Field(
        ...,
        title="Port",
        description="The port number of the proxy server",
    )
    proxy_type: ProxyTypes = Field(
        ...,
        title="Proxy Type",
        description="The type of the proxy server",
        alias="proxyType",
    )
    proxy_name: str = Field(
        ...,
        title="Proxy Name",
        description="A user-defined name for the proxy",
        alias="proxyName",
    )


####################### User Agent Models #######################


class FetchUserAgentsResponseModel(BaseModel):
    """The FetchUserAgentsResponseModel defines the structure of the response for fetching user agent configurations."""

    model_config = ConfigDict(
        title="Fetch User Agents Response Model",
        description="Model representing the response for fetching user agent configurations",
        populate_by_name=True,
    )

    id: UUID = Field(
        ...,
        title="User Agent Id",
        description="Unique identifier for the user agent",
    )
    user_agent: str = Field(
        ...,
        title="User Agent",
        description="The user agent string",
        alias="userAgent",
    )
    type: UserAgentTypes = Field(
        ...,
        title="User Agent Type",
        description="The type/category of the user agent",
    )
    agent_browser: str = Field(
        ...,
        title="Agent Browser",
        description="The browser associated with the user agent",
        alias="agentBrowser",
    )
    agent_os: str = Field(
        ...,
        title="Agent Operating System",
        description="The operating system associated with the user agent",
        alias="agentOS",
    )
