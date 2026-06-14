import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base

# Import all models so SQLAlchemy can register them
from app.models.customer import Customer
from app.models.segment import Segment
from app.models.campaign import Campaign
from app.models.communication import CommunicationLog

from app.routers import analytics, campaigns, customers, receipts, segments

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xenocrm")

app = FastAPI(
    title="XenoCRM",
    description="AI-native Mini CRM for BrewCo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    Create database tables automatically if they don't exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created/verified successfully")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} ({duration:.3f}s)"
    )

    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


# Routers
app.include_router(customers.router)
app.include_router(segments.router)
app.include_router(campaigns.router)
app.include_router(receipts.router)
app.include_router(analytics.router)