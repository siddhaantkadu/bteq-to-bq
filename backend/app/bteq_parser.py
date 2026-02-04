import re
from dataclasses import dataclass
from typing import List, Literal

TokenType = Literal["BTEQ_CMD", "SQL"]

@dataclass
class Block:
    kind: TokenType
    text: str
    line_start: int
    line_end: int

_BTEQ_CMD = re.compile(r"^\s*\.\w+", re.IGNORECASE)

def parse_bteq(script: str) -> List[Block]:
    lines = script.splitlines()
    blocks: List[Block] = []
    sql_buf = []
    sql_start_line = 1

    def flush_sql(end_line: int):
        nonlocal sql_buf, sql_start_line
        sql_text = "\n".join(sql_buf).strip()
        if sql_text:
            for stmt, a, b in split_sql_statements(sql_text, sql_start_line):
                blocks.append(Block(kind="SQL", text=stmt, line_start=a, line_end=b))
        sql_buf = []

    for i, line in enumerate(lines, start=1):
        if _BTEQ_CMD.match(line):
            flush_sql(i - 1)
            blocks.append(Block(kind="BTEQ_CMD", text=line.rstrip(), line_start=i, line_end=i))
            sql_start_line = i + 1
        else:
            sql_buf.append(line)

    flush_sql(len(lines))
    return blocks

def split_sql_statements(sql_text: str, start_line: int):
    # split on ';' not inside single quotes
    stmts = []
    buf = []
    in_str = False
    line = start_line
    stmt_start_line = start_line

    for ch in sql_text:
        if ch == "\n":
            line += 1
        if ch == "'" and (not buf or buf[-1] != "\\"):
            in_str = not in_str
        if ch == ";" and not in_str:
            stmt = "".join(buf).strip()
            if stmt:
                stmts.append((stmt + ";", stmt_start_line, line))
            buf = []
            stmt_start_line = line
        else:
            buf.append(ch)

    tail = "".join(buf).strip()
    if tail:
        stmts.append((tail, stmt_start_line, line))
    return stmts