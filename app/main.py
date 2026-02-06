from __future__ import annotations
import logging
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .config import settings
from .mapping import load_mapping_csv, apply_table_mapping
from .translator import convert_sql

logger = logging.getLogger(__name__)

app = FastAPI(title="bteq-to-bq-backend", version="1.0.0")

class ConvertRequest(BaseModel):
    sql: str = Field(..., description="Teradata SQL input")
    mapping_csv: str | None = Field(default=None, description="Optional mapping CSV path on server")
    enable_ai_fallback: bool = True

class ConvertResponse(BaseModel):
    bigquery_sql: str
    used: str
    issues: list[str]

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/v1/convert", response_model=ConvertResponse)
def convert(req: ConvertRequest):
    outcome = convert_sql(req.sql, project=settings.gcp_project, enable_ai=req.enable_ai_fallback)
    out_sql = outcome.sql
    if req.mapping_csv:
        mappings = load_mapping_csv(req.mapping_csv)
        out_sql = apply_table_mapping(out_sql, mappings)
    return ConvertResponse(bigquery_sql=out_sql, used=outcome.used, issues=outcome.issues)
