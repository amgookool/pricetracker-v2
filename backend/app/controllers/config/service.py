from typing import List, Optional

from app.config.db import (
    Session,
    get_all,
    get_all_by_field,
    get_by_field,
    get_by_id,
    get_db_session,
)
from app.config.logger import get_logger
from app.schemas.configs import (
    DESKTOP_UA,
    PROXY_SERVERS,
    ProxiesTable,
    ProxyTypes,
    UserAgentsTable,
    UserAgentTypes,
)

# Initialize logger
logger = get_logger(__name__)


def seed_user_agents():
    """Seed the user_agents table with predefined desktop user agents."""
    with get_db_session() as session:
        existing_agents = get_all(session, UserAgentsTable)
        if existing_agents:
            logger.info("User agents already seeded. Skipping seeding process.")
            return

        logger.info("Seeding user agents into the database.")
        for ua_entry in DESKTOP_UA:
            ua_record = UserAgentsTable(
                user_agent=ua_entry["agent"],
                agent_browser=ua_entry["browser"],
                agent_os=ua_entry["os"],
                type=UserAgentTypes.DESKTOP,
            )
            session.add(ua_record)
        session.commit()
        logger.info("User agents seeding completed successfully.")


def seed_proxies():
    """Seed the proxies table with predefined proxy servers."""
    with get_db_session() as session:
        existing_proxies = get_all(session, ProxiesTable)
        if existing_proxies:
            logger.info("Proxies already seeded. Skipping seeding process.")
            return

        logger.info("Seeding proxies into the database.")
        for proxy_entry in PROXY_SERVERS:
            proxy_record = ProxiesTable(
                proxy_name=proxy_entry["name"],
                ip_address=proxy_entry["ip"],
                port=proxy_entry["port"],
                username=proxy_entry.get("username"),
                password=proxy_entry.get("password"),
                proxy_type=ProxyTypes(proxy_entry["type"]),
            )
            session.add(proxy_record)
        session.commit()
        logger.info("Proxies seeding completed successfully.")


def get_all_proxies(session: Session) -> List[ProxiesTable]:
    """Retrieve all proxy configuration from the database"""
    try:
        data = get_all(session, ProxiesTable)
        return data
    except Exception as e:
        logger.exception("Error retrieving proxies: %s", e)
        raise e


def get_all_user_agents(session: Session) -> List[UserAgentsTable]:
    """Retrieve all user agents from the database"""
    try:
        data = get_all(session, UserAgentsTable)
        return data
    except Exception as e:
        logger.exception("Error retrieving user agents: %s", e)
        raise e
