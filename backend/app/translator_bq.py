from google.cloud import bigquery_migration_v2

class BQTranslator:
    def __init__(self, project: str, location: str):
        self.project = project
        self.location = location
        self.client = bigquery_migration_v2.SqlTranslationServiceClient()

    def translate(self, sql: str, source_dialect: str = "TERADATA") -> str:
        parent = f"projects/{self.project}/locations/{self.location}"
        resp = self.client.translate_sql(
            request=bigquery_migration_v2.TranslateSqlRequest(
                parent=parent,
                source_dialect=source_dialect,
                query=sql,
            )
        )
        return resp.translation or ""