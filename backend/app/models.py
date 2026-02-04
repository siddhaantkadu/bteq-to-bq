from pydantic import BaseModel, Field
from typing import Optional, List, Literal

Method = Literal["BQ_TRANSLATOR", "AI_FALLBACK", "SKIPPED"]

class ConnectionConfig(BaseModel):
    gcp_project: str = Field(min_length=1)
    gcp_location: str = Field(default="us")
    gcs_bucket: str = Field(min_length=1)
    vertex_model: str = Field(default="gemini-1.5-pro")

class JobRequest(BaseModel):
    script_text: str = Field(min_length=1)
    source_dialect: str = Field(default="TERADATA")  # translator source dialect
    keep_bteq_cmds_as_comments: bool = Field(default=True)

class ItemReport(BaseModel):
    line_start: int
    line_end: int
    method: Method
    ok: bool
    error: Optional[str] = None
    input_sql: str
    output_sql: str

class JobResponse(BaseModel):
    job_id: str
    translated_sql: str
    items: List[ItemReport]