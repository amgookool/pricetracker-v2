from datetime import timedelta
from typing import Annotated, List

from app.config.db import Session, get_session
from app.config.logger import get_logger
from app.config.settings import get_settings
from app.controllers.auth.models import UserResponseModel
from app.middleware.auth import get_access_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .models import FetchProxiesResponseModel, FetchUserAgentsResponseModel
from .service import get_all_proxies, get_all_user_agents

# FastAPI Router
router = APIRouter()

# Logger
logger = get_logger(__name__)

# Environment Vars
SETTINGS = get_settings()


@router.get(
    "/proxies",
    tags=["Configuration"],
    summary="Get all proxy configurations",
    description="Retrieve all proxy configurations from the database.",
    response_model=List[FetchProxiesResponseModel],
)
async def get_proxies(
    active_user: Annotated[UserResponseModel, Depends(get_access_user)],
    session: Annotated[Session, Depends(get_session)],
):
    try:
        proxies = get_all_proxies(session)

        proxies_response = [
            FetchProxiesResponseModel(
                id=proxy.id,
                ipAddress=proxy.ip_address,
                port=proxy.port,
                proxyType=proxy.proxy_type,
                proxyName=proxy.proxy_name,
            )
            for proxy in proxies
        ]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[
                prox.model_dump(mode="json", by_alias=True) for prox in proxies_response
            ],
        )
    except HTTPException as http_e:
        logger.error("HTTP error while fetching proxies: %s", http_e.detail)
        raise http_e
    except Exception as general_e:
        logger.exception("Error fetching proxies: %s", general_e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching proxies.",
        )


@router.get(
    "/user-agents",
    tags=["Configuration"],
    summary="Get all user agents",
    description="Retrieve all user agents from the database.",
)
async def get_user_agents(
    active_user: Annotated[UserResponseModel, Depends(get_access_user)],
    session: Annotated[Session, Depends(get_session)],
):
    try:
        user_agents = get_all_user_agents(session)

        user_agents_response = [
            FetchUserAgentsResponseModel(
                id=ua.id,
                user_agent=ua.user_agent,
                agent_browser=ua.agent_browser,
                agent_os=ua.agent_os,
                type=ua.type,
            )
            for ua in user_agents
        ]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[
                ua.model_dump(mode="json", by_alias=True) for ua in user_agents_response
            ],
        )
    except HTTPException as http_e:
        logger.error("HTTP error while fetching user agents: %s", http_e.detail)
        raise http_e
    except Exception as general_e:
        logger.exception("Error fetching user agents: %s", general_e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user agents.",
        )
