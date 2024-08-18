from pydantic_settings import BaseSettings;

class Settings(BaseSettings):
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRES_IN: int
    REFRESH_TOKEN_EXPIRES_IN: int
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    JWT_ALGORITHM: str
    JWT_HEX32: str

    class Config:
        env_file = '.env'

settings = Settings()