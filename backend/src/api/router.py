from fastapi import APIRouter

from src.api.files.router import router as files_router

api_router = APIRouter(prefix="/api")

api_router.include_router(files_router)
