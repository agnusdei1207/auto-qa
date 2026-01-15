"""
AI QA Brain - Multi-Agent Web Automation System

Autonomous web testing with AI-powered test generation and execution.
"""
import os
import sys
import logging
import asyncio
import httpx
from threading import Thread
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_libs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs'))
if _libs_path not in sys.path:
    sys.path.insert(0, _libs_path)

from libs.database.src import repository as db
from apps.brain.src.core.loop import run_brain_loop
from apps.brain.src.config import OLLAMA_API_URL, LLM_MODEL

app = FastAPI(title="Enhanced AI QA Brain", version="2.0")

brain_running = False
current_thread: Optional[Thread] = None
current_session_id: Optional[str] = None


class StartTestRequest(BaseModel):
    url: str
    domain_info: str


def check_running() -> bool:
    return brain_running


@app.on_event("startup")
async def startup_event():
    logger.info(f"🧠 Enhanced QA Brain v2.0 - AI-Powered Web Testing with Parallel Execution")
    logger.info(f"Using model: {LLM_MODEL}")
    logger.info(f"Max parallel agents: {os.environ.get('MAX_PARALLEL_AGENTS', '4')}")
    logger.info(f"Git auto-commit: {os.environ.get('ENABLE_GIT_AUTO_COMMIT', 'false')}")

    logger.info("Initializing database...")
    init_success = db.init_database()
    if init_success:
        logger.info("✅ Database initialized successfully")
    else:
        logger.warning("⚠️  Database initialization failed, will retry on first use")

    await pull_model()


async def pull_model():
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(f"{OLLAMA_API_URL}/api/pull", json={"name": LLM_MODEL})
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning(f"Failed to pull model: {e}")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Enhanced Brain",
        "version": "2.0",
        "features": [
            "async_parallel_execution",
            "resource_monitoring",
            "safe_cleanup",
            "git_auto_commit"
        ]
    }


@app.get("/status")
async def status():
    return {
        "running": brain_running,
        "session_id": current_session_id,
        "model": LLM_MODEL
    }


@app.post("/start")
async def start_test(request: StartTestRequest):
    global brain_running, current_thread, current_session_id

    if brain_running:
        return {"status": "error", "message": "Test already running"}

    current_session_id = db.create_session(request.url, request.domain_info)

    if not current_session_id:
        return {"status": "error", "message": "Failed to create session"}

    brain_running = True
    logger.info(f"🚀 Starting Enhanced QA test on {request.url} (session: {current_session_id})")

    current_thread = Thread(
        target=run_brain_loop,
        args=(current_session_id, request.url, request.domain_info, check_running),
        daemon=True
    )
    current_thread.start()

    return {
        "status": "success",
        "message": "Enhanced QA test started",
        "session_id": current_session_id
    }


@app.post("/stop")
async def stop_test():
    global brain_running
    if not brain_running:
        return {"status": "error", "message": "No test running"}

    logger.info("⏹️  Stopping QA test...")
    brain_running = False

    if current_session_id:
        db.end_session(current_session_id, "STOPPED")

    return {"status": "success", "message": "Test stopped"}
