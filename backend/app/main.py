import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.routers import admin, hospitals, prices, procedures, stats

logger = logging.getLogger(__name__)

_HOSPITAL_MIGRATIONS = [
    "ALTER TABLE hospitals ADD COLUMN npi VARCHAR(10)",
    "ALTER TABLE hospitals ADD COLUMN phone VARCHAR(20)",
    "ALTER TABLE hospitals ADD COLUMN website VARCHAR(500)",
    "ALTER TABLE hospitals ADD COLUMN booking_url VARCHAR(500)",
    "ALTER TABLE hospitals ADD COLUMN facility_type VARCHAR(50)",
    "ALTER TABLE hospitals ADD COLUMN has_3d_mammography BOOLEAN",
    "ALTER TABLE hospitals ADD COLUMN acr_accredited BOOLEAN",
    "ALTER TABLE hospitals ADD COLUMN accepts_new_patients BOOLEAN",
    "ALTER TABLE hospitals ADD COLUMN availability_note VARCHAR(255)",
    "ALTER TABLE hospitals ADD COLUMN accepted_insurances JSON",
]


def _run_migrations(engine):
    with engine.connect() as conn:
        for stmt in _HOSPITAL_MIGRATIONS:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # column already exists


@asynccontextmanager
async def lifespan(app):
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    _run_migrations(engine)
    yield


app = FastAPI(title="Healthcare Price Transparency", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(procedures.router, prefix="/api/v1")
app.include_router(prices.router, prefix="/api/v1")
app.include_router(hospitals.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
