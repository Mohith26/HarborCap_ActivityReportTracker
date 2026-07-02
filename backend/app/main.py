import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, properties, reports, deals, availabilities, metrics, insights
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 - register all models on Base.metadata

# Initialise schema + upload dir on boot. There are no Alembic migrations yet,
# so create_all is the source of truth for the (fresh) deploy database. It is
# idempotent — only missing tables are created.
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HarborCap Activity Report Tracker", version="1.0.0")

_cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(properties.router, prefix="/api/properties", tags=["properties"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(deals.router, prefix="/api", tags=["deals"])
app.include_router(availabilities.router, prefix="/api", tags=["availabilities"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(insights.router, prefix="/api", tags=["insights"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
