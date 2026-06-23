from fastapi import FastAPI

from arrivia_recs.api.routes.health import router as health_router
from arrivia_recs.api.routes.recommendations import router as recommendations_router
from arrivia_recs.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Internal multi-tenant travel recommendations service for AI concierge use cases.",
    )
    app.include_router(health_router)
    app.include_router(recommendations_router, prefix="/v1", tags=["recommendations"])
    return app


app = create_app()
