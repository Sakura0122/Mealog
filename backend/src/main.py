from fastapi import FastAPI

from src.api.router import api_router
from src.core.logger import setup_logger
from src.handlers.exception import register_exception_handlers

setup_logger()

app = FastAPI(title="Mealog食刻")

register_exception_handlers(app)
app.include_router(api_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
