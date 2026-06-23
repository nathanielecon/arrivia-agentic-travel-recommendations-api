def response_body_snippet(text: str, max_len: int = 512) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"
