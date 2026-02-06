from __future__ import annotations
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

@dataclass(frozen=True)
class TableMapping:
    td_database: str
    td_table: str
    bq_project: str
    bq_dataset: str
    bq_table: str

    def bq_fqn(self) -> str:
        return f"`{self.bq_project}.{self.bq_dataset}.{self.bq_table}`"

def load_mapping_csv(path: str | Path) -> list[TableMapping]:
    p = Path(path)
    rows: list[TableMapping] = []
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"td_database","td_table","bq_project","bq_dataset","bq_table"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Mapping CSV missing columns: {sorted(missing)}")
        for r in reader:
            rows.append(TableMapping(
                td_database=(r["td_database"] or "").strip(),
                td_table=(r["td_table"] or "").strip(),
                bq_project=(r["bq_project"] or "").strip(),
                bq_dataset=(r["bq_dataset"] or "").strip(),
                bq_table=(r["bq_table"] or "").strip(),
            ))
    return rows

def apply_table_mapping(sql: str, mappings: Iterable[TableMapping]) -> str:
    out = sql
    for m in mappings:
        if not (m.td_database and m.td_table and m.bq_project and m.bq_dataset and m.bq_table):
            continue
        db = re.escape(m.td_database)
        tb = re.escape(m.td_table)
        patterns = [
            rf'(?i)(?<![\w`]){db}\s*\.\s*{tb}(?![\w`])',
            rf'(?i)"{db}"\s*\.\s*"{tb}"',
            rf'(?i)\[{db}\]\s*\.\s*\[{tb}\]',
        ]
        for pat in patterns:
            out = re.sub(pat, m.bq_fqn(), out)
    return out
