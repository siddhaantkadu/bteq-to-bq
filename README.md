# BTEQ to BigQuery Converter (BigQuery Translator + AI Fallback)

This repository contains a full-stack application that converts Teradata BTEQ scripts into BigQuery GoogleSQL using a two-step approach:
1) BigQuery SQL Translation API (primary, rule-based)
2) Vertex AI (Gemini) fallback when translation fails, looks incomplete, or does not validate

The application also validates translated SQL using BigQuery dry-run to confirm syntax correctness without scanning data.

---

## Features

- React UI (Vite) with file upload and paste editor
- Connection settings screen in UI (GCP Project, Location, GCS Bucket, Vertex Model)
- FastAPI backend for translation and reporting
- BigQuery Translator first, Vertex AI fallback second
- BigQuery dry-run validation
- Per-statement conversion report (method, status, errors)
- Docker Compose for local run

---

## Repository Structure

bteq-to-bq/
frontend/               # React UI (Vite)
backend/                # FastAPI backend
docker-compose.yml
README.md

Backend modules:
- backend/app/bteq_parser.py: parses BTEQ and splits SQL statements
- backend/app/translator_bq.py: BigQuery SQL Translation API client
- backend/app/translator_ai.py: Vertex AI (Gemini) fallback translator
- backend/app/validator.py: BigQuery dry-run validator
- backend/app/config.py: runtime config (defaults from env; can be overridden from UI)
- backend/app/report.py: heuristics to detect incomplete translation

---

## How It Works

1) The input BTEQ script is parsed into:
   - BTEQ control commands (lines starting with '.' such as .LOGON, .SET, .IF ERRORCODE)
   - SQL statements
2) BTEQ control commands are kept as comments for manual/orchestration handling.
3) Each SQL statement is processed:
   - Translate using BigQuery SQL Translation API
   - If translation fails, is incomplete, or fails dry-run validation, translate using Vertex AI (Gemini)
4) Translated SQL is validated using BigQuery dry-run.
5) The final result includes:
   - One translated BigQuery SQL output
   - A conversion report per statement

---

## Prerequisites

### Local requirements (recommended)
- Docker and Docker Compose

### Alternative (non-Docker)
- Python 3.11+
- Node.js 20+

### Google Cloud requirements
A Google Cloud project with these APIs enabled:
- BigQuery API
- BigQuery Migration / SQL Translation API
- Vertex AI API
- (Optional) Cloud Storage API

You also need a Service Account with appropriate IAM roles.

---

## 1) Google Cloud Setup

### 1.1 Enable required APIs

Using gcloud:

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable bigquerymigration.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

1.2 Create a Service Account

Replace PROJECT_ID with your project id:

gcloud iam service-accounts create bteq-bq-converter \
  --project PROJECT_ID \
  --display-name "BTEQ to BigQuery Converter"

1.3 Assign IAM roles

Minimum required roles:
	•	roles/bigquery.jobUser (BigQuery dry-run validation)
	•	roles/bigquerymigration.user (SQL Translation API)
	•	roles/aiplatform.user (Vertex AI fallback)

Optional:
	•	roles/storage.objectAdmin (future enhancement: save outputs to GCS)

Replace PROJECT_ID with your project id:

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:bteq-bq-converter@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:bteq-bq-converter@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquerymigration.user"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:bteq-bq-converter@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:bteq-bq-converter@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

1.4 Create a Service Account key (local development only)

gcloud iam service-accounts keys create key.json \
  --iam-account=bteq-bq-converter@PROJECT_ID.iam.gserviceaccount.com

Security note:
	•	Do not commit this key to Git.
	•	Store it under secrets/key.json locally.

⸻

2) Run Locally with Docker (Recommended)

2.1 Prepare secrets

From repo root:

mkdir -p secrets
cp /path/to/key.json ./secrets/key.json

2.2 Create .env file

Create .env in repo root:

GCP_PROJECT=your-project-id
GCP_LOCATION=us
GCS_BUCKET=your-bucket-name
VERTEX_MODEL=gemini-1.5-pro

Notes:
	•	GCS_BUCKET is required by the UI config screen even if you do not store files to GCS yet.
	•	You can set any existing bucket in your project.

2.3 Start the application

docker compose up --build

2.4 Access the application
	•	Frontend UI: http://localhost:3000
	•	Backend health: http://localhost:8000/health

⸻

3) Configure Connection Settings in the UI

Open the UI and go to the Connection tab. Fill and save:
	•	GCP Project: your Google Cloud project id
	•	Location: example ‘us’
	•	GCS Bucket: bucket name (reserved for future saving artifacts)
	•	Vertex Model: example ‘gemini-1.5-pro’

Important:
	•	Do not enter credentials in the UI.
	•	Credentials are loaded from the service account key mounted via GOOGLE_APPLICATION_CREDENTIALS.

Current behavior:
	•	UI settings are stored in memory in the backend and reset when the backend restarts.
	•	For production, persist config in a database or Secret Manager.

⸻

4) Convert a BTEQ Script

Option A: Upload file
	•	Upload .bteq, .sql, or .txt
	•	Click Convert

Option B: Paste script
	•	Paste BTEQ into the editor
	•	Click Convert

Output:
	•	Translated BigQuery SQL appears in the output panel.
	•	Conversion report table shows per statement method:
	•	BQ_TRANSLATOR: BigQuery Translation API used
	•	AI_FALLBACK: Vertex AI used
	•	SKIPPED: BTEQ command preserved as comment

You can download the translated SQL from the UI.

⸻

5) Run Without Docker (Development Mode)

5.1 Backend

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GCP_PROJECT=your-project-id
export GCP_LOCATION=us
export GCS_BUCKET=your-bucket-name
export VERTEX_MODEL=gemini-1.5-pro
export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/key.json

uvicorn app.main:app --reload --port 8000

5.2 Frontend

cd frontend
npm install
npm run dev

Open:
	•	http://localhost:3000

⸻

6) Environment Variables

The backend reads defaults from environment variables, and the UI can override them at runtime.
	•	GCP_PROJECT: Google Cloud project id
	•	GCP_LOCATION: location, default ‘us’
	•	GCS_BUCKET: bucket name (required by UI config screen)
	•	VERTEX_MODEL: Vertex AI model name, default ‘gemini-1.5-pro’
	•	GOOGLE_APPLICATION_CREDENTIALS: path to the JSON key file

Docker Compose sets:
	•	GOOGLE_APPLICATION_CREDENTIALS=/secrets/key.json

⸻

7) Git Publishing Checklist

7.1 Add .gitignore

Create .gitignore in repo root:

secrets/
.env
node_modules/
dist/
__pycache__/
.venv/
*.pyc

7.2 Ensure secrets are not committed

Do not commit:
	•	secrets/key.json
	•	any other credential JSON files
	•	.env file

⸻

8) Troubleshooting

8.1 PermissionDenied errors

Common causes:
	•	Missing IAM roles on the service account
	•	Wrong service account key file mounted
	•	Wrong project or location

Fix:
	•	Verify roles:
	•	roles/bigquery.jobUser
	•	roles/bigquerymigration.user
	•	roles/aiplatform.user
	•	Verify Docker is using the correct key file:
	•	secrets/key.json
	•	Verify the correct project and location in UI Connection settings

8.2 Vertex AI model not available

Causes:
	•	Organization policy restricts models
	•	Region restrictions

Fix:
	•	Try another model name in UI:
	•	gemini-1.5-pro
	•	gemini-1.5-flash
	•	Ensure Vertex AI API enabled and service account has roles/aiplatform.user

8.3 BigQuery dry-run validation fails

This means the translated SQL is not valid BigQuery SQL.
	•	Check the conversion report row for the error message.
	•	If even AI fallback fails, manual review is required for that statement.

8.4 Connection settings reset after restart

Current implementation stores configuration in memory.
For production, persist config in:
	•	Firestore, Cloud SQL, Redis
	•	or a file-based config with a mounted volume

⸻

9) Security Notes
	•	Do not store credentials in the UI.
	•	Do not commit service account keys or secrets.
	•	Use Workload Identity / default service account in production instead of JSON keys.

⸻

10) Known Limitations
	•	BTEQ control flow (.IF ERRORCODE, .GOTO, .LABEL) is not executable in BigQuery SQL and is preserved as comments.
	•	.IMPORT and .EXPORT are not automatically converted to BigQuery load/extract jobs.
	•	Some Teradata-specific syntax may still require manual review even after AI fallback.

⸻

11) Recommended Production Setup
	•	Backend: Cloud Run
	•	Frontend: Cloud Run or Cloud Storage + CDN
	•	Credentials: Workload Identity (no JSON keys)
	•	Add authentication (IAP or OAuth)
	•	Persist configuration and job results in a database
	•	Add job queue and async processing for large scripts



