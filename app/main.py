from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions.base import DomainException
from app.core.exceptions.handlers import (
    global_domain_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.core.middlewares import ASGILoggingMiddleware
from app.domains.market_data.api.routers import router as market_data_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Data is now served via PostgreSQL, so we don't load pandas dataframes here anymore.
    yield


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Estate Intelligence",
        description="API for Real Estate Data Visualization using DDD and Supabase",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ASGILoggingMiddleware)

    # Register Global Exception Handlers (RFC 9457)
    app.add_exception_handler(DomainException, global_domain_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    app.include_router(market_data_router, prefix="/api")

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "Welcome to the Immobilier API. Visit /docs for the API reference."}

    return app


app = create_app()
