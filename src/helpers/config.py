from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NAME: str
    MONGO_URL: str
    DATABASE: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def get_settings():
    return Settings()
