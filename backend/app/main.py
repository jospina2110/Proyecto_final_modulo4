from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.database import init_database
from app.config.settings import settings
from app.middlewares.exception_handlers import register_exception_handlers
from app.routes import appointments, doctors, patients


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    servers=[{"url": "/api", "description": "Proxy nginx del frontend"}],
)
register_exception_handlers(app)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)


@app.get("/health", tags=["Estado"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
