from typing import Union

from fastapi import APIRouter, Depends

from helpers.config import Settings, get_settings

settings = get_settings()

base_router = APIRouter()


@base_router.get("/")
async def read_root(app_settings: Settings = Depends(get_settings)):
    return {"Hello": app_settings.NAME}


@base_router.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
