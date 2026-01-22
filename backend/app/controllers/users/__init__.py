from app.config.settings import get_settings
from fastapi import APIRouter

# FastAPI Router
router = APIRouter()

# Environment Vars
SETTINGS = get_settings()
