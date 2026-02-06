from __future__ import annotations

import argparse
import json
import logging

from .config import settings
from .service import convert_single_file, convert_folder

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="bteq2bq", description="Teradata SQL -> BigQuery SQL converter (BQ translator + AI fallback)")
    parser.add_argument("--project", default=settings.gcp_project, help="GCP project id (or set env GCP_PROJECT)")
    parser.add_argument("--no-ai", action="store_true", help="Disable Vertex AI fallback")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("convert", help="Convert a single SQL file")
    p1.add_argument("--input", required=True)
    p1.add_argument("--output", required=False)
    p1.add_argument("--inplace", action="store_true")
    p1.add_argument("--mapping", required=False)

    p2 = sub.add_parser("bulk", help="Convert all SQL files under a folder")
    p2.add_argument("--input-dir", required=True)
    p2.add_argument("--output-dir", required=False)
    p2.add_argument("--inplace", action="store_true")
    p2.add_argument("--mapping", required=False)
    p2.add_argument("--report", default="report.json")

    args = parser.parse_args(argv)
    enable_ai = not args.no_ai

    if args.cmd == "convert":
        if not args.inplace and not args.output:
            parser.error("--output is required unless --inplace")
        out = args.output or args.input
        outcome = convert_single_file(args.input, out, args.project, args.mapping, args.inplace, enable_ai)
        print(json.dumps({"used": outcome.used, "issues": outcome.issues, "output": out}, indent=2))
        return 0

    if args.cmd == "bulk":
        if not args.inplace and not args.output_dir:
            parser.error("--output-dir is required unless --inplace")
        out_dir = args.output_dir or args.input_dir
        report = convert_folder(args.input_dir, out_dir, args.project, args.mapping, args.inplace, enable_ai)
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump({"total": report.total, "ok": report.ok, "failed": report.failed, "details": report.details}, f, indent=2)
        print(json.dumps({"total": report.total, "ok": report.ok, "failed": report.failed, "report": args.report}, indent=2))
        return 0

    return 2

if __name__ == "__main__":
    raise SystemExit(main())
