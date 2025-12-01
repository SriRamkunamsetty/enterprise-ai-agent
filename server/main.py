# server/main.py
import os
import uvicorn
import logging
import asyncio
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict

from agents.supervisor import SupervisorAgent
from observability.tracing import setup_tracing
from memory.memory_bank import MemoryBank

logger = logging.getLogger("enterprise_ai_server")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# init observability if configured
setup_tracing()

app = FastAPI(title="Enterprise AI Agent")

# single supervisor instance
supervisor = SupervisorAgent()
memory = MemoryBank()

class RunRequest(BaseModel):
    task: str
    params: Dict[str, Any] = {}

@app.post("/run")
async def run(req: RunRequest):
    session = {}
    result = await supervisor.on_message({"task": req.task, "params": req.params}, session)
    # if reporter attached a report_str, store it
    report_str = result.get("report_str") if isinstance(result, dict) else None
    if report_str:
        key = f"report:{req.params.get('symbol','unknown')}:{req.params.get('month','unknown')}"
        memory.put(key, report_str)
    return result

# A2A-style adapter endpoint: accept A2A-style JSON -> call supervisor
@app.post("/a2a/run")
async def a2a_run(req: Request):
    payload = await req.json()
    # attempt to extract message
    message = payload.get("message") or payload
    session = {}  # can be enriched
    result = await supervisor.on_message(message, session)
    return {"task_updates": result}

@app.get("/memory/{prefix}")
def query_memory(prefix: str):
    return memory.query_by_prefix(prefix)

if __name__ == "__main__":
    uvicorn.run("server.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), reload=False)