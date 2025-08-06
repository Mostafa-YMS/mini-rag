from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class FileChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    content: str = Field(..., min_length=1)
    metadata: dict
    order: int = Field(..., gt=0)
    project_id: ObjectId

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],
                "name": "chunk_project_id_index",
                "unique": False,
            },
        ]
