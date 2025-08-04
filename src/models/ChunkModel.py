from bson.objectid import ObjectId
from pymongo import InsertOne

from .BaseModel import BaseModel
from .schemas import FileChunk


class ChunkModel(BaseModel):
    def __init__(self, db: object):
        super().__init__(db)
        self.model = FileChunk
        self.collection = self.db.file_chunks

    async def create_chunk(self, chunk: FileChunk):
        return await self.collection.insert_one(
            chunk.model_dump(by_alias=True, exclude_unset=True)
        )

    async def get_chunk(self, chunk_id: str):
        return await self.collection.find_one({"_id": ObjectId(chunk_id)})

    async def get_all_chunks(self, project_id: str, page: int = 1, limit: int = 12):
        count = await self.collection.count_documents({})
        pages = count // limit if count % limit == 0 else (count // limit) + 1

        cursor = (
            self.collection.find({"project_id": project_id})
            .skip((page - 1) * limit)
            .limit(limit)
        )

        chunks = []
        async for chunk in cursor:
            chunks.append(FileChunk(**chunk))

        return {"chunks": chunks, "count": count, "pages": pages, "limit": limit}

    async def create_bulk_chunks(self, chunks: list, batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: str):
        return await self.collection.delete_many({"project_id": project_id})
