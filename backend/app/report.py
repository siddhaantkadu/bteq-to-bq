def looks_incomplete(translated: str) -> bool:
    """
    Heuristic to decide whether BigQuery translator output is incomplete.
    Tune this as you see real outputs.
    """
    t = (translated or "").lower()
    if not translated.strip():
        return True
    if "todo" in t:
        return True
    if "not supported" in t:
        return True
    return False