from pydantic_settings import BaseSettings


class Settings(BaseSettings, object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    NAME: str
    MONGO_URL: str
    DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None

    MAX_INPUT_CHARS: int = None
    GENERATION_MAX_TOKENS: int = None
    GENERATION_TEMPERATURE: float = None

    VDB_BACKEND: str
    VDB_PATH: str
    VDB_DISTANCE_METHOD: str = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def get_settings():
    return Settings()
