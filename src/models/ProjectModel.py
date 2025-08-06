from .BaseModel import BaseModel
from .schemas import Project


class ProjectModel(BaseModel):
    def __init__(self, db: object):
        super().__init__(db=db)
        self.collection = self.db.projects

    @classmethod
    async def create_instance(cls, db: object):
        instance = cls(db=db)
        await instance.__init_collection()
        return instance

    async def __init_collection(self):
        all_collections = await self.db.list_collection_names()
        if "projects" not in all_collections:
            self.collection = self.db.projects
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    keys=index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_project(self, project: Project):
        return await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_unset=True)
        )

    async def get_or_create_project(self, project_id: str):
        project = await self.collection.find_one({"project_id": project_id})

        if project is None:
            project = Project(project_id=project_id)
            await self.create_project(project)
            return project

        return Project(**project)

    async def get_all_projects(self, page: int = 1, limit: int = 12):
        count = await self.collection.count_documents({})
        pages = count // limit if count % limit == 0 else (count // limit) + 1

        cursor = self.collection.find().skip((page - 1) * limit).limit(limit)

        projects = []
        async for project in cursor:
            projects.append(Project(**project))

        return {"projects": projects, "count": count, "pages": pages, "limit": limit}
