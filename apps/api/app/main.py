import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.core.rate_limit import setup_rate_limiting
from app.middleware.logging import RequestLoggingMiddleware
from app.tasks.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    start_scheduler()
    print("Application starting up...")
    yield
    print("Shutting down...")

app = FastAPI(
    title=settings.app_name,
    description="Bike Auction API",
    version="1.0.0",
    lifespan=lifespan,
)

setup_rate_limiting(app)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "environment": "simplified"}

# Mount feature routers
app.include_router(api_router, prefix="/api/v1")
