from fastapi import APIRouter

from src.api.auth.router import router as auth_router
from src.api.files.router import router as files_router
from src.api.meal_records.router import router as meal_records_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(files_router)
api_router.include_router(meal_records_router)
