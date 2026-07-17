"""
app/main.py
===========
FastAPI application entrypoint for the ClimateSense AI Backend.

Responsibilities:
- Construct and configure the FastAPI application instance.
- Compile the LangGraph pipeline exactly once at startup and store the
  compiled graph on ``app.state.graph`` so request handlers can reuse it
  without rebuilding the graph on every call.
- Configure CORS for local frontend development.
- Expose lightweight liveness endpoints (`/` and `/health`).
- Mount the versioned API router from `app.api.routes`.
- Fail fast and loudly if graph construction fails at startup.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.graph.builder import build_graph
from app.api.routes import router as api_router
from app.api.routers import auth, carbon, users
from app.core.config import settings

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Local frontend origins allowed for CORS during development
# ---------------------------------------------------------------------------

LOCAL_DEV_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    settings.FRONTEND_URL,
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown for the FastAPI app.

    On startup, this compiles the LangGraph pipeline exactly once via
    ``build_graph()`` and attaches the compiled graph to ``app.state.graph``.
    If graph construction fails, the exception is logged and re-raised so
    that the application does not start in a broken, unusable state.

    Args:
        app: The FastAPI application instance whose lifespan is managed.

    Yields:
        None: Control is yielded back to FastAPI once startup completes
        successfully; teardown logic (if any) runs after the yield.

    Raises:
        RuntimeError: If the LangGraph pipeline fails to compile.
    """
    logger.info("ClimateSense AI Backend starting up...")
    try:
        app.state.graph = build_graph()
        logger.info("LangGraph pipeline compiled and attached to app.state.graph.")
    except Exception as exc:
        logger.error(f"Startup failed: could not build LangGraph pipeline: {exc}", exc_info=True)
        raise RuntimeError(f"Application startup failed during graph construction: {exc}") from exc

    yield

    logger.info("ClimateSense AI Backend shutting down...")


def create_app() -> FastAPI:
    """Construct and configure the ClimateSense AI FastAPI application.

    Returns:
        FastAPI: A fully configured FastAPI application instance, with
        CORS middleware, the API router, and the lifespan handler attached.
    """
    app = FastAPI(
        title="ClimateSense AI Backend",
        description="Backend service exposing the ClimateSense AI LangGraph pipeline.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(dict.fromkeys(LOCAL_DEV_ORIGINS)),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(
        _request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.error("Database error: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=503,
            content={"detail": "Database is unavailable"},
        )

    app.include_router(api_router)
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api", tags=["Users"])
    app.include_router(carbon.router, prefix="/api", tags=["Carbon Engine"])

    return app


app = create_app()


@app.get("/", tags=["Meta"])
async def root() -> Dict[str, str]:
    """Return a simple liveness message for the backend root endpoint.

    Returns:
        Dict[str, str]: A confirmation message indicating the service is running.
    """
    return {"message": "ClimateSense AI Backend Running"}


@app.get("/health", tags=["Meta"])
async def health() -> Dict[str, str]:
    """Return the health status of the backend service.

    Returns:
        Dict[str, str]: A simple status payload used for health checks.
    """
    return {"status": "healthy"}
