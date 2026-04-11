from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/taco_index"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = "placeholder"
    poll_interval_minutes: int = 15
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
