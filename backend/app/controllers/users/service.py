from app.config.db import get_by_field, get_db_session
from app.config.logger import get_logger
from app.config.settings import get_settings
from app.controllers.auth.services import get_password_hash
from app.schemas.users import UserRole, UsersTable

# Logger
logger = get_logger(__name__)

# Environment Vars
SETTINGS = get_settings()


def create_admin_user():
    """Create an initial admin user if it does not exist."""
    with get_db_session() as session:
        # Check if admin user exists
        admin_exists = get_by_field(
            session, UsersTable, "username", SETTINGS.ADMIN_USER
        )
        if not admin_exists:
            logger.info("Creating initial admin user: %s", SETTINGS.ADMIN_USER)
            hashed_password = get_password_hash(SETTINGS.ADMIN_PASSWORD)
            admin_user = UsersTable(
                name="Administrator",
                username=SETTINGS.ADMIN_USER,
                password=hashed_password,
                role=UserRole.ADMIN,
                force_password_change=False,
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            return admin_user
        else:
            logger.info("Admin user already exists, skipping creation")
            return admin_exists
