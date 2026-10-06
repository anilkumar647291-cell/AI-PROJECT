import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow", case_sensitive=True)

    PROJECT_NAME: str = "AI Adaptive Tourism Companion"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "ai-adaptive-tourism-companion-secret-key-3.13-fastapi"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./tourism_companion.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # External APIs (optional for full external live sync)
    OPENWEATHER_API_KEY: str = ""
    MAPS_API_KEY: str = ""
    AI_API_KEY: str = ""

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

settings = Settings()
