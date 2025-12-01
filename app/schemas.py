# app/schemas.py
from pydantic import BaseModel
from typing import Any, Dict, Optional

class TaskRequest(BaseModel):
    task: str
    params: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    task_id: str
    status: str
    queued: bool

class TaskResult(BaseModel):
    task_id: str
    result: Optional[Dict[str, Any]] = None
    status: str
    error: Optional[str] = None