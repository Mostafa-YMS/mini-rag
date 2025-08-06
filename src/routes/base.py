from fastapi import APIRouter, Depends

from helpers.config import Settings, get_settings

settings = get_settings()

base_router = APIRouter()


@base_router.get("/")
async def read_root(app_settings: Settings = Depends(get_settings)):
    return {"Hello": app_settings.NAME}
