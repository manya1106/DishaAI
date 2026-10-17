from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "local"
    DATA_MODE: str = "snapshot"
    DATABASE_URL: Optional[str] = None
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    LLM_ENABLED: bool = False
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.1-8b-instant"
    LLM_TIMEOUT_S: int = 12
    RATE_LIMIT_CHAT_PER_MIN: int = 20
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
