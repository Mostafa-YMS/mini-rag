from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from helpers.config import get_settings
from routes import base, files


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.db = app.mongodb_conn[settings.DATABASE]

    yield  # Application runs during this time

    # Shutdown
    app.mongodb_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(files.files_router)
