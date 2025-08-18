from fastapi import Depends

from controllers.BaseController import BaseController

from .providers import *
from .VDBEnums import VDBEnums


class VDBFactory:
    def __init__(
        self, config, base_controller: BaseController = Depends(BaseController)
    ):
        self.config = config
        self.base_controller = base_controller

    def create(self, provider: str):
        if provider == VDBEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(
                db_name=self.config["VDB_PATH"]
            )
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config["VDB_DISTANCE_METHOD"],
            )

        return None
