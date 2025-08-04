from helpers.config import get_settings, Settings


class BaseModel:
    def __init__(self, db: object):
        self.db = db
        self.app_settings: Settings = get_settings()
