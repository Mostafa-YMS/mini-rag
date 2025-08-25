from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from helpers.config import get_settings
from routes import *
from stores.llm import LLMProviderFactory
from stores.vdb.VDBFactory import VDBFactory


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

    vdb_factory = VDBFactory(settings.model_dump())
    app.vdb_client = vdb_factory.create(provider=settings.VDB_BACKEND)
    app.vdb_client.connect()

    yield

    # Shutdown
    app.mongodb_conn.close()
    app.vdb_client.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(base_router)
app.include_router(files_router)
app.include_router(nlp_router)
