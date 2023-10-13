from typing import Any


def get_http_header(bearer_key: str = "xyz") -> dict[str, Any]:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_key}",
    }

