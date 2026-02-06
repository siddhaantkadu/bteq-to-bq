from __future__ import annotations
import re
from dataclasses import dataclass

TERADATA_LEFTOVERS = [
    "VOLATILE", "PRIMARY INDEX", "MULTISET", "NO PRIMARY INDEX", "LOCKING ROW",
    "COLLECT STATISTICS", "BTET", ".LOGON", ".LOGOFF", ".GOTO",
]

@dataclass
class ValidationResult:
    ok: bool
    issues: list[str]

def basic_bq_sanity(sql: str) -> ValidationResult:
    issues: list[str] = []
    u = sql.upper()

    for token in TERADATA_LEFTOVERS:
        if token in u:
            issues.append(f"Contains Teradata/BTEQ token: {token}")

    if re.search(r"(?m)^\s*\.(LOGON|LOGOFF|IF|GOTO|RUN|QUIT)\b", sql, flags=re.IGNORECASE):
        issues.append("Contains BTEQ dot-commands (expects SQL, not BTEQ control flow).")

    if not sql.strip():
        issues.append("Empty output SQL.")

    return ValidationResult(ok=(len(issues) == 0), issues=issues)
