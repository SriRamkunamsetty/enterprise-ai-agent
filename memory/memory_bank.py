# memory/memory_bank.py
import json
import os
import threading
from typing import Any, Dict, Optional

DEFAULT_DB = os.path.expanduser("~/.enterprise_ai_memory.json")
_lock = threading.Lock()

class MemoryBank:
    def __init__(self, path: Optional[str] = None):
        self.path = path or DEFAULT_DB
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def _read(self) -> Dict[str, Any]:
        with _lock:
            with open(self.path, "r") as f:
                return json.load(f)

    def _write(self, data: Dict[str, Any]):
        with _lock:
            with open(self.path, "w") as f:
                json.dump(data, f, indent=2, default=str)

    def put(self, key: str, value: Any):
        data = self._read()
        data[key] = value
        self._write(data)

    def get(self, key: str) -> Optional[Any]:
        data = self._read()
        return data.get(key)

    def query_by_prefix(self, prefix: str):
        data = self._read()
        return {k: v for k, v in data.items() if k.startswith(prefix)}