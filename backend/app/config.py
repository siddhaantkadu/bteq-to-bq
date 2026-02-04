from pydantic import BaseModel, Field
import os

class AppConfig(BaseModel):
    gcp_project: str = Field(default_factory=lambda: os.environ.get("GCP_PROJECT", ""))
    gcp_location: str = Field(default_factory=lambda: os.environ.get("GCP_LOCATION", "us"))
    gcs_bucket: str = Field(default_factory=lambda: os.environ.get("GCS_BUCKET", ""))
    vertex_model: str = Field(default_factory=lambda: os.environ.get("VERTEX_MODEL", "gemini-1.5-pro"))

# In-memory config (simple). Replace with DB/Redis in prod.
CONFIG = AppConfig()