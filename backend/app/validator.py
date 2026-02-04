from google.cloud import bigquery

class BQValidator:
    def __init__(self, project: str):
        self.client = bigquery.Client(project=project)

    def dry_run_ok(self, sql: str) -> tuple[bool, str]:
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        try:
            self.client.query(sql, job_config=job_config)
            return True, ""
        except Exception as e:
            return False, str(e)