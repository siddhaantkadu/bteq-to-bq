from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .mapping import apply_table_mapping, load_mapping_csv
from .translator import convert_sql, TranslateOutcome
from .io_utils import read_text, write_text, iter_sql_files

@dataclass
class ConvertReport:
    total: int
    ok: int
    failed: int
    details: list[dict]

def _apply_mapping_if_any(sql: str, mapping_csv: Optional[str]) -> str:
    if not mapping_csv:
        return sql
    mappings = load_mapping_csv(mapping_csv)
    return apply_table_mapping(sql, mappings)

def convert_single_file(input_path: str, output_path: str, project: Optional[str], mapping_csv: Optional[str], inplace: bool=False, enable_ai: bool=True) -> TranslateOutcome:
    src = Path(input_path)
    dst = src if inplace else Path(output_path)

    sql = read_text(src)
    outcome = convert_sql(sql, project=project, enable_ai=enable_ai)
    final_sql = _apply_mapping_if_any(outcome.sql, mapping_csv) if outcome.sql else ""

    if final_sql:
        write_text(dst, final_sql)

    return TranslateOutcome(sql=final_sql, used=outcome.used, issues=outcome.issues)

def convert_folder(input_dir: str, output_dir: str, project: Optional[str], mapping_csv: Optional[str], inplace: bool=False, enable_ai: bool=True) -> ConvertReport:
    src_root = Path(input_dir)
    dst_root = Path(output_dir)
    files = list(iter_sql_files(src_root))

    details = []
    ok = failed = 0

    for f in files:
        rel = f.relative_to(src_root)
        out_path = f if inplace else (dst_root / rel)
        try:
            sql = read_text(f)
            outcome = convert_sql(sql, project=project, enable_ai=enable_ai)
            final_sql = _apply_mapping_if_any(outcome.sql, mapping_csv) if outcome.sql else ""
            if final_sql:
                write_text(out_path, final_sql)
                ok += 1
                status = "ok"
            else:
                failed += 1
                status = "failed"
            details.append({
                "file": str(f),
                "out": str(out_path),
                "status": status,
                "used": outcome.used,
                "issues": outcome.issues,
            })
        except Exception as e:
            failed += 1
            details.append({
                "file": str(f),
                "out": str(out_path),
                "status": "failed",
                "used": "n/a",
                "issues": [f"{type(e).__name__}: {e}"],
            })

    return ConvertReport(total=len(files), ok=ok, failed=failed, details=details)
