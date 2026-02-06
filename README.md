# bteq-to-bq-backend (Teradata SQL -> BigQuery SQL backend)

This backend converts Teradata SQL to BigQuery Standard SQL using a **two-stage** strategy:

1. **BigQuery Migration Translation API** (primary)
2. **Vertex AI (Gemini) fallback** when translator fails or output looks invalid

It supports:
- **Single file** conversion
- **Bulk folder** conversion (mirrors directory structure)
- Optional **mapping CSV** to rewrite table references:
  `td_database,td_table,bq_project,bq_dataset,bq_table`

Auth:
- **No service account keys** required. Works with **ADC**:
  - Local: `gcloud auth application-default login`
  - CI (GitHub Actions): **WIF** (Workload Identity Federation) -> ADC

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Authenticate locally (ADC)
gcloud auth application-default login

# Convert a single file
python -m app.cli convert --input ./examples/in.sql --output ./out.sql

# Convert a folder (bulk)
python -m app.cli bulk --input-dir ./examples/sql --output-dir ./out_sql

# With mapping (rewrite table names)
python -m app.cli bulk --input-dir ./examples/sql --output-dir ./out_sql --mapping ./mapping.csv
```

## Docker

Build:
```bash
docker build -t bteq2bq-backend .
```

Run CLI inside container (mount working directory + your ADC):
```bash
docker run --rm -it \
  -v "$PWD":/work \
  -v "$HOME/.config/gcloud":/gcloud:ro \
  -e CLOUDSDK_CONFIG=/gcloud \
  -e GCP_PROJECT=project-a9be9c09-ee2e-4b2b-817 \
  bteq2bq-backend \
  python -m app.cli bulk --input-dir /work/in --output-dir /work/out --mapping /work/mapping.csv
```

## API (optional)

Run:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Then POST:
- `POST /v1/convert` with `{ "sql": "...", "mapping_csv": null }`

