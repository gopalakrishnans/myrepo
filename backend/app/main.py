from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import hospitals, prices, procedures, stats


@asynccontextmanager
async def lifespan(app):
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Healthcare Price Transparency", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(procedures.router, prefix="/api/v1")
app.include_router(prices.router, prefix="/api/v1")
app.include_router(hospitals.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
