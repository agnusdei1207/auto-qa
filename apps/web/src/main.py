"""
Web UI - Dashboard Interface
"""
import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_libs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs'))
if _libs_path not in sys.path:
    sys.path.insert(0, _libs_path)

from libs.database.src import repository as db

app = FastAPI(title="Auto-QA Dashboard", version="0.1")

_current_dir = os.path.dirname(os.path.abspath(__file__))
_templates_dir = os.path.join(_current_dir, "..", "templates")
templates = Jinja2Templates(directory=_templates_dir)

_static_dir = os.path.join(_current_dir, "..", "static")
if os.path.exists(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

BRAIN_API_URL = os.environ.get('BRAIN_API_URL', 'http://brain:9000')


class StartTestRequest(BaseModel):
    url: str
    domain_info: str


@app.on_event("startup")
async def startup():
    logger.info("🌐 Web UI started")


@app.get("/")
async def index(request: Request):
    """Dashboard page."""
    sessions = db.get_all_sessions(limit=10)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sessions": sessions
    })


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Web UI"}


@app.get("/api/sessions")
async def get_sessions():
    """Get all test sessions."""
    return db.get_all_sessions(limit=50)


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/api/start")
async def start_test(request: StartTestRequest):
    """Start a new test."""
    async with httpx.AsyncClient(timeout=300) as client:
        try:
            response = await client.post(
                f"{BRAIN_API_URL}/start",
                json={"url": request.url, "domain_info": request.domain_info}
            )
            response.raise_for_status()
            logger.info(f"Started test: {response.json()}")
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Start test error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stop")
async def stop_test():
    """Stop current test."""
    async with httpx.AsyncClient(timeout=300) as client:
        try:
            response = await client.post(f"{BRAIN_API_URL}/stop")
            response.raise_for_status()
            logger.info("Stopped test")
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Stop test error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Get current test status."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(f"{BRAIN_API_URL}/status")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Status check error: {e}")
            return {"running": False, "error": str(e)}
