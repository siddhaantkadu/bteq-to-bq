from vertexai.generative_models import GenerativeModel

SYSTEM_RULES = """You convert Teradata BTEQ / Teradata SQL into BigQuery GoogleSQL.

Rules:
- Output ONLY BigQuery SQL (GoogleSQL). No explanations.
- Preserve semantics (filters, joins, null handling, casting).
- Replace Teradata-specific syntax with BigQuery equivalents.
- Preserve identifiers; do not invent tables/columns.
- If something cannot be safely translated, add a comment line:
  -- TODO: manual review needed
  right above that statement.
"""

class AITranslator:
    def __init__(self, model_name: str):
        self.model = GenerativeModel(model_name)

    def translate(self, sql: str) -> str:
        prompt = f"{SYSTEM_RULES}\n\nINPUT:\n{sql}\n\nOUTPUT:\n"
        resp = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.0,
                "max_output_tokens": 8192
            },
        )
        return (resp.text or "").strip()