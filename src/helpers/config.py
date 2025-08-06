from pydantic_settings import BaseSettings


class Settings(BaseSettings, object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    NAME: str
    MONGO_URL: str
    DATABASE: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def get_settings():
    return Settings()
