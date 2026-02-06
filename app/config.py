from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    gcp_project: str | None = Field(default=None, alias="GCP_PROJECT")

    vertex_location: str = Field(default="us-central1", alias="VERTEX_LOCATION")
    vertex_model: str = Field(default="gemini-1.5-pro", alias="VERTEX_MODEL")

    enable_ai_fallback: bool = Field(default=True, alias="ENABLE_AI_FALLBACK")
    max_sql_chars: int = Field(default=400_000, alias="MAX_SQL_CHARS")

settings = Settings()
