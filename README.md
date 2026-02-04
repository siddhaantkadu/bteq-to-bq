# BTEQ → BigQuery Converter

Converts Teradata BTEQ scripts into BigQuery GoogleSQL:
1) BigQuery SQL Translator API first
2) Vertex AI Gemini fallback if translator fails / incomplete
3) BigQuery dry-run validation

## Prerequisites
- Google Cloud project with APIs enabled:
  - BigQuery
  - BigQuery Migration / SQL Translation
  - Vertex AI
- Service account permissions:
  - BigQuery Job User
  - BigQuery Migration User
  - Vertex AI User
  - (Optional) Storage Object Admin (future: saving outputs to GCS)

## Local run with Docker

1) Create `secrets/` and place your service account key:
   - `secrets/key.json`

2) Create `.env` in repo root: