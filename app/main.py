from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    app.include_router(market_data_router, prefix="/api")

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "Welcome to the Immobilier API. Visit /docs for the API reference."}

    return app


app = create_app()
