from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from helpers.config import get_settings
from routes import base, files
from stores.llm import LLMProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.db = app.mongodb_conn[settings.DATABASE]

    llm_factory = LLMProviderFactory(settings.model_dump())
    app.generation_client = llm_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE
    )

    yield  # Application runs during this time

    # Shutdown
    app.mongodb_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(files.files_router)
