from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://xenocrm:xenocrm@localhost:5432/xenocrm"
    redis_url: str = "redis://localhost:6379"
    groq_api_key: str = ""

    channel_stub_url: str = "http://localhost:8001"
    crm_base_url: str = "http://localhost:8000"

    # Allow both local frontend and Railway frontend
    cors_origins: str = (
        "http://localhost:5173,"
        "https://crm-application-production-3229.up.railway.app"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()