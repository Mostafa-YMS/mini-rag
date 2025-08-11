from datetime import datetime, timezone
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: ObjectId
    type: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    size: int = Field(ge=0, default=None)
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    config: dict = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],
                "name": "asset_project_id_index",
                "unique": False,
            },
            {
                "key": [("name", 1), ("project_id", 1)],
                "name": "asset_name_project_id_index",
                "unique": True,
            },
        ]
