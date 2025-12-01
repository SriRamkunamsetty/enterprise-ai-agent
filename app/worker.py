# app/worker.py
import asyncio
import uuid
import logging
from typing import Dict, Any, Optional
from agents.supervisor import SupervisorAgent  # uses your fixed SupervisorAgent
from app.schemas import TaskResult

logger = logging.getLogger(__name__)

class BackgroundAgentRunner:
    def __init__(self, concurrency: int = 4):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, TaskResult] = {}
        self.semaphore = asyncio.Semaphore(concurrency)
        self._runner_task: Optional[asyncio.Task] = None
        self.agent = SupervisorAgent()

    async def start(self):
        logger.info("Starting BackgroundAgentRunner")
        if self._runner_task is None or self._runner_task.done():
            self._runner_task = asyncio.create_task(self._worker_loop())

    async def shutdown(self):
        logger.info("Shutting down BackgroundAgentRunner")
        if self._runner_task:
            self._runner_task.cancel()
            try:
                await self._runner_task
            except asyncio.CancelledError:
                logger.info("Runner task cancelled")

    async def submit(self, message: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        self.results[task_id] = TaskResult(task_id=task_id, status="queued")
        await self.queue.put((task_id, message))
        return task_id

    async def _worker_loop(self):
        while True:
            task_id, message = await self.queue.get()
            logger.info("Dequeued task %s", task_id)
            asyncio.create_task(self._run_task(task_id, message))

    async def _run_task(self, task_id: str, message: Dict[str, Any]):
        async with self.semaphore:
            logger.info("Running task %s", task_id)
            self.results[task_id].status = "running"
            try:
                # session can carry metadata; empty for now
                session = {}
                result = await self.agent.on_message(message, session)
                self.results[task_id].result = result if isinstance(result, dict) else {"result": result}
                self.results[task_id].status = "done"
            except Exception as e:
                logger.exception("Task %s failed: %s", task_id, e)
                self.results[task_id].error = str(e)
                self.results[task_id].status = "error"

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        return self.results.get(task_id)