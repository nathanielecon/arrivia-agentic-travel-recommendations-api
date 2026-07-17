from contextlib import asynccontextmanager

from fastapi import FastAPI

from arrivia_recs.api.deps import close_upstream_clients
from arrivia_recs.api.routes.health import router as health_router
from arrivia_recs.api.routes.metrics import router as metrics_router
from arrivia_recs.api.routes.recommendations import router as recommendations_router
from arrivia_recs.config import settings
from arrivia_recs.observability import configure_logging
from arrivia_recs.observability.middleware import RequestContextMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await close_upstream_clients()


def create_app() -> FastAPI:
    configure_logging(getattr(settings, "log_level", "INFO"))
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Internal multi-tenant travel recommendations service for AI concierge use cases.",
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    app.include_router(health_router)
    if getattr(settings, "metrics_enabled", True):
        app.include_router(metrics_router)
    app.include_router(recommendations_router, prefix="/v1", tags=["recommendations"])
    return app


app = create_app()
