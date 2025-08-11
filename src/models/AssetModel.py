from bson import ObjectId

from .BaseModel import BaseModel
from .schemas import Asset


class AssetModel(BaseModel):
    def __init__(self, db: object):
        super().__init__(db=db)
        self.collection = self.db.assets

    @classmethod
    async def create_instance(cls, db: object):
        instance = cls(db=db)
        await instance.__init_collection()
        return instance

    async def __init_collection(self):
        all_collections = await self.db.list_collection_names()
        if "assets" not in all_collections:
            self.collection = self.db.assets
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    keys=index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_asset(self, asset: Asset):
        res = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_unset=True)
        )
        asset.id = res.inserted_id
        return asset

    async def get_project_assets(self, project_id: str):
        return await self.collection.find(
            {
                "project_id": (
                    ObjectId(project_id) if isinstance(project_id, str) else project_id
                )
            }
        ).to_list(length=None)
