from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, properties, reports, deals, availabilities, metrics, insights

app = FastAPI(title="HarborCap Activity Report Tracker", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
