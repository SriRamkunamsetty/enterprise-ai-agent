# tools/openapi_tool.py
import requests
from typing import Any, Dict

class OpenAPITool:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def call(self, path: str, payload: Dict[str, Any]):
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()