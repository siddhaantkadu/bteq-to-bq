# app/translator.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from .config import settings
from .validators import basic_bq_sanity

logger = logging.getLogger(__name__)


@dataclass
class TranslateOutcome:
    sql: str
    used: str  # "bq_translator" | "vertex_ai"
    issues: list[str]


def _unwrap_retry_error(e: Exception) -> str:
    """
    Tenacity wraps the real exception in RetryError.
    This returns the underlying exception message so troubleshooting is easy.
    """
    try:
        last = getattr(e, "last_attempt", None)
        if last and last.exception():
            inner = last.exception()
            return f"{type(inner).__name__}: {inner}"
    except Exception:
        pass
    return f"{type(e).__name__}: {e}"


@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=1, max=10))
def translate_with_bq_migration(sql: str, project: str) -> str:
    """
    BigQuery Migration Translation API (compatible across google-cloud-bigquery-migration versions).
    """
    from google.cloud import bigquery_migration_v2  # type: ignore

    client = bigquery_migration_v2.MigrationServiceClient()
    parent = f"projects/{project}/locations/us"

    # Requests/enums can live in different places depending on version.
    types = getattr(bigquery_migration_v2, "types", None)

    # Prefer module-level enums if present, else use types.*
    SrcEnum = getattr(bigquery_migration_v2, "SqlTranslationSourceDialect", None)
    TgtEnum = getattr(bigquery_migration_v2, "SqlTranslationTargetDialect", None)

    if SrcEnum is None and types is not None:
        SrcEnum = getattr(types, "SqlTranslationSourceDialect", None)
    if TgtEnum is None and types is not None:
        TgtEnum = getattr(types, "SqlTranslationTargetDialect", None)

    if SrcEnum is None or TgtEnum is None:
        raise RuntimeError(
            "Could not locate SqlTranslationSourceDialect/TargetDialect enums in bigquery_migration_v2. "
            "Please check installed google-cloud-bigquery-migration version."
        )

    src = SrcEnum.TERADATA
    tgt = TgtEnum.BIGQUERY

    # Call translate_query with kwargs (avoids request class differences)
    resp = client.translate_query(
        parent=parent,
        source_dialect=src,
        target_dialect=tgt,
        query=sql,
    )
    return getattr(resp, "translated_query", "") or ""


@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=1, max=20))
def translate_with_vertex_ai(sql: str, project: str) -> str:
    """
    Vertex AI Gemini fallback: returns SQL ONLY.
    """
    import vertexai  # type: ignore
    from vertexai.generative_models import GenerativeModel, GenerationConfig  # type: ignore

    vertexai.init(project=project, location=settings.vertex_location)
    model = GenerativeModel(settings.vertex_model)

    prompt = (
        "You are a senior SQL migration engineer. Convert Teradata SQL to BigQuery Standard SQL. "
        "Preserve semantics. Output ONLY the converted SQL, no explanations, no markdown.\n\n"
        f"TERADATA SQL:\n{sql}\n\nBIGQUERY SQL ONLY:"
    )

    cfg = GenerationConfig(
        temperature=0.1,
        max_output_tokens=8192,
    )
    resp = model.generate_content(prompt, generation_config=cfg)
    return (resp.text or "").strip()


def convert_sql(sql: str, project: Optional[str], enable_ai: bool = True) -> TranslateOutcome:
    project = project or settings.gcp_project
    if not project:
        raise ValueError("GCP project is required. Set env GCP_PROJECT or pass --project.")
    if len(sql) > settings.max_sql_chars:
        raise ValueError(
            f"Input SQL too large ({len(sql)} chars). Increase MAX_SQL_CHARS if intended."
        )

    issues: list[str] = []

    # 1) Try BigQuery Migration translator
    try:
        translated = translate_with_bq_migration(sql, project=project)
        v = basic_bq_sanity(translated)

        if translated.strip() and v.ok:
            return TranslateOutcome(sql=translated, used="bq_translator", issues=[])

        issues += (v.issues if translated.strip() else ["Translator returned empty output."])
        logger.warning("BQ translator produced issues: %s", issues)
    except Exception as e:
        msg = _unwrap_retry_error(e)
        issues.append(f"BQ translator failed: {msg}")
        logger.warning("BQ translator exception: %s", msg)

    # 2) Vertex AI fallback
    if not enable_ai or not settings.enable_ai_fallback:
        return TranslateOutcome(sql="", used="bq_translator", issues=issues + ["AI fallback disabled."])

    try:
        ai_sql = translate_with_vertex_ai(sql, project=project)
        v2 = basic_bq_sanity(ai_sql)

        if v2.ok and ai_sql.strip():
            return TranslateOutcome(sql=ai_sql, used="vertex_ai", issues=issues)

        return TranslateOutcome(
            sql=ai_sql,
            used="vertex_ai",
            issues=issues + v2.issues,
        )
    except Exception as e:
        msg = _unwrap_retry_error(e)
        return TranslateOutcome(
            sql="",
            used="vertex_ai",
            issues=issues + [f"Vertex AI failed: {msg}"],
        )