"""
Playwright Executor - Refactored Web Automation Service

Simplified main module using separated components:
- browser_manager.py: Browser state management
- action_handlers.py: Action execution logic
- requests.py: Request/response models
"""
import json
import logging
from pathlib import Path
from fastapi import FastAPI
from apps.executor.src.browser_manager import BrowserManager
from apps.executor.src.action_handlers import ActionHandlers
from apps.executor.src.requests import (
    NavigateRequest, FillRequest, SelectRequest,
    ClickRequest, HoverRequest, DragRequest, ScrollRequest,
    ScreenshotRequest, SetHeadfulRequest, GetHTMLRequest,
    ProgressUpdateRequest
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Playwright Executor", version="2.0")

# Initialize components
screenshots_dir = Path("/tmp/screenshots")
screenshots_dir.mkdir(parents=True, exist_ok=True)

browser_manager = BrowserManager(screenshots_dir)
action_handlers = ActionHandlers(browser_manager, screenshots_dir)


@app.on_event("startup")
async def startup():
    logger.info("🎭 Playwright Executor v2.0 started")


@app.on_event("shutdown")
async def shutdown():
    await browser_manager.cleanup_all()
    logger.info("Playwright Executor stopped")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Executor", "version": "2.0"}


# Browser Actions
@app.post("/navigate")
async def navigate(request: NavigateRequest):
    return await action_handlers.navigate(request)


@app.post("/fill")
async def fill(request: FillRequest):
    return await action_handlers.fill(request)


@app.post("/select")
async def select_option(request: SelectRequest):
    return await action_handlers.select_option(request)


@app.post("/click")
async def click(request: ClickRequest):
    return await action_handlers.click(request)


@app.post("/hover")
async def hover(request: HoverRequest):
    return await action_handlers.hover(request)


@app.post("/double_click")
async def double_click(request: ClickRequest):
    return await action_handlers.double_click(request)


@app.post("/drag")
async def drag(request: DragRequest):
    return await action_handlers.drag(request)


@app.post("/scroll")
async def scroll(request: ScrollRequest):
    return await action_handlers.scroll(request)


@app.post("/submit")
async def submit(request: ClickRequest):
    return await action_handlers.submit(request)


# Verification
@app.post("/verify_text")
async def verify_text(request: dict):
    return await action_handlers.verify_text(request.get("session_id"), request.get("text", ""))


@app.post("/verify_element")
async def verify_element(request: dict):
    return await action_handlers.verify_element(request.get("session_id"), request.get("selector", ""))


@app.post("/verify_url")
async def verify_url(request: dict):
    return await action_handlers.verify_url(request.get("session_id"), request.get("expected_url", ""))


@app.post("/verify_title")
async def verify_title(request: dict):
    return await action_handlers.verify_title(request.get("session_id"), request.get("expected_title", ""))


# Enhanced Features
@app.post("/set_headful")
async def set_headful(request: SetHeadfulRequest):
    return await action_handlers.set_headful(request)


@app.post("/screenshot")
async def screenshot(request: ScreenshotRequest):
    return await action_handlers.screenshot(request)


@app.post("/screenshot_base64")
async def screenshot_base64(request: ScreenshotRequest):
    return await action_handlers.screenshot_base64(request)


@app.post("/get_html")
async def get_html(request: GetHTMLRequest):
    return await action_handlers.get_html(request)


@app.post("/update_progress")
async def update_progress(request: ProgressUpdateRequest):
    return await action_handlers.update_progress(request)


@app.get("/progress/{session_id}")
async def get_progress(session_id: str):
    try:
        session_file = screenshots_dir / f"{session_id}_progress.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                return json.load(f)
        else:
            return {"message": "No progress data yet"}
    except Exception as e:
        logger.error(f"Get progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
async def cleanup_session(session_id: str):
    """Cleanup browser session"""
    await browser_manager.cleanup_session(session_id)
    return {"success": True, "message": f"Session {session_id} cleaned up"}
