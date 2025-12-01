# app/main.py
import os
import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from app.schemas import TaskRequest, TaskResponse, TaskResult
from app.logging_config import configure_logging
from app.worker import BackgroundAgentRunner

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
configure_logging(LOG_LEVEL)
logger = logging.getLogger("enterprise.api")

app = FastAPI(title="Enterprise AI Agent API", version="1.0.0")

# Allow CORS if needed - adjust origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
)

# single runner instance (module-level)
runner: BackgroundAgentRunner = BackgroundAgentRunner(concurrency=int(os.getenv("CONCURRENCY", "4")))

@app.on_event("startup")
async def startup_event():
    logger.info("Starting app...")
    await runner.start()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down app...")
    await runner.shutdown()

@app.post("/v1/tasks", response_model=TaskResponse)
async def submit_task(req: TaskRequest):
    message = req.dict()
    task_id = await runner.submit(message)
    return TaskResponse(task_id=task_id, status="queued", queued=True)

@app.get("/v1/tasks/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    r = runner.get_result(task_id)
    if r is None:
        raise HTTPException(status_code=404, detail="task_id not found")
    return r

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.get("/ready")
async def ready():
    # simple readiness: runner exists and agent constructed
    try:
        _ = runner.agent
        return JSONResponse({"ready": True})
    except Exception:
        raise HTTPException(status_code=500, detail="not ready")