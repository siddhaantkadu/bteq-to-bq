import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CONFIG, AppConfig
from .models import ConnectionConfig, JobRequest, JobResponse, ItemReport
from .bteq_parser import parse_bteq
from .translator_bq import BQTranslator
from .translator_ai import AITranslator
from .validator import BQValidator
from .report import looks_incomplete

app = FastAPI(title="BTEQ → BigQuery Converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # lock down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/config", response_model=AppConfig)
def get_config():
    return CONFIG

@app.post("/api/config", response_model=AppConfig)
def set_config(cfg: ConnectionConfig):
    # Update in-memory config
    CONFIG.gcp_project = cfg.gcp_project
    CONFIG.gcp_location = cfg.gcp_location
    CONFIG.gcs_bucket = cfg.gcs_bucket
    CONFIG.vertex_model = cfg.vertex_model
    return CONFIG

@app.post("/api/jobs", response_model=JobResponse)
def create_job(req: JobRequest):
    job_id = str(uuid.uuid4())

    blocks = parse_bteq(req.script_text)

    bq_translator = BQTranslator(CONFIG.gcp_project, CONFIG.gcp_location)
    ai_translator = AITranslator(CONFIG.vertex_model)
    validator = BQValidator(CONFIG.gcp_project)

    out_parts = []
    items: list[ItemReport] = []

    for blk in blocks:
        if blk.kind == "BTEQ_CMD":
            if req.keep_bteq_cmds_as_comments:
                commented = f"-- BTEQ_CMD (manual): {blk.text}"
                out_parts.append(commented)
                items.append(ItemReport(
                    line_start=blk.line_start,
                    line_end=blk.line_end,
                    method="SKIPPED",
                    ok=True,
                    error=None,
                    input_sql=blk.text,
                    output_sql=commented
                ))
            else:
                items.append(ItemReport(
                    line_start=blk.line_start,
                    line_end=blk.line_end,
                    method="SKIPPED",
                    ok=True,
                    error=None,
                    input_sql=blk.text,
                    output_sql=""
                ))
            continue

        # 1) Try BigQuery translator
        bq_out = ""
        bq_ok = False
        bq_err = ""
        try:
            bq_out = bq_translator.translate(blk.text, source_dialect=req.source_dialect)
            if bq_out and not bq_out.strip().endswith(";") and blk.text.strip().endswith(";"):
                bq_out = bq_out.rstrip() + ";"
            bq_ok, bq_err = validator.dry_run_ok(bq_out)
        except Exception as e:
            bq_ok, bq_err = False, str(e)

        # Decide if AI fallback is needed
        if (not bq_ok) or looks_incomplete(bq_out):
            ai_out = ai_translator.translate(blk.text)
            if ai_out and not ai_out.strip().endswith(";") and blk.text.strip().endswith(";"):
                ai_out = ai_out.rstrip() + ";"
            ai_ok, ai_err = validator.dry_run_ok(ai_out)

            out_parts.append(ai_out)
            items.append(ItemReport(
                line_start=blk.line_start,
                line_end=blk.line_end,
                method="AI_FALLBACK",
                ok=ai_ok,
                error=ai_err if not ai_ok else None,
                input_sql=blk.text,
                output_sql=ai_out
            ))
        else:
            out_parts.append(bq_out)
            items.append(ItemReport(
                line_start=blk.line_start,
                line_end=blk.line_end,
                method="BQ_TRANSLATOR",
                ok=True,
                error=None,
                input_sql=blk.text,
                output_sql=bq_out
            ))

    translated_sql = "\n\n".join([p for p in out_parts if p is not None])
    return JobResponse(job_id=job_id, translated_sql=translated_sql, items=items)

@app.get("/health")
def health():
    return {"status": "ok"}