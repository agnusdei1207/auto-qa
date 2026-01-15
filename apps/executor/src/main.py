"""
Playwright Executor - Web Automation Service

Executes browser actions (click, fill, drag, etc.) using Playwright.
Supports headful mode for visible testing and screenshot streaming.
"""
import os
import logging
import asyncio
import base64
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Playwright Executor", version="0.1")

# Browser state management
browsers = {}
contexts = {}
screenshots_dir = Path("/tmp/screenshots")
screenshots_dir.mkdir(parents=True, exist_ok=True)

# Session configuration
session_configs = {}


class NavigateRequest(BaseModel):
    url: str
    session_id: str


class FillRequest(BaseModel):
    selector: str
    value: str
    session_id: str


class SelectRequest(BaseModel):
    selector: str
    value: str
    session_id: str


class ClickRequest(BaseModel):
    selector: str
    session_id: str


class HoverRequest(BaseModel):
    selector: str
    session_id: str


class DragRequest(BaseModel):
    source: str
    target: str
    session_id: str


class ScrollRequest(BaseModel):
    direction: str
    amount: int
    session_id: str


class ScreenshotRequest(BaseModel):
    session_id: str
    full_page: bool = False


class SetHeadfulRequest(BaseModel):
    session_id: str
    headful: bool = True


class GetHTMLRequest(BaseModel):
    session_id: str


class ProgressUpdateRequest(BaseModel):
    session_id: str
    test_case_id: str
    step_number: int
    status: str
    message: str


@app.on_event("startup")
async def startup():
    logger.info("🎭 Playwright Executor started")


@app.on_event("shutdown")
async def shutdown():
    for browser in browsers.values():
        await browser.close()
    logger.info("Playwright Executor stopped")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Executor"}


async def get_context(session_id: str, headful: bool = False):
    """Get or create browser context for session."""
    if session_id not in contexts:
        if "browser" not in browsers:
            browser_obj = await async_playwright().start()
            browsers["browser"] = browser_obj

        browser = browsers["browser"]
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"
        )
        page = await context.new_page()

        if headful:
            logger.info(f"👁️  Headful mode enabled for session {session_id}")

        contexts[session_id] = {
            "context": context,
            "page": page,
            "headful": headful
        }

        session_configs[session_id] = {
            "headful": headful,
            "created_at": datetime.now().isoformat(),
            "steps_completed": 0
        }

        logger.info(f"Created new context for session {session_id} (headful={headful})")

    return contexts[session_id]


@app.post("/navigate")
async def navigate(request: NavigateRequest):
    try:
        ctx = await get_context(request.session_id)
        await ctx["page"].goto(request.url, wait_until="networkidle", timeout=30000)
        logger.info(f"Navigated to {request.url}")
        return {"success": True, "url": request.url}
    except Exception as e:
        logger.error(f"Navigate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fill")
async def fill(request: FillRequest):
    try:
        ctx = await get_context(request.session_id)
        await ctx["page"].fill(request.selector, request.value, timeout=10000)
        logger.info(f"Filled {request.selector} with {request.value}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Fill error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/select")
async def select_option(request: SelectRequest):
    try:
        ctx = await get_context(request.session_id)
        await ctx["page"].select_option(request.selector, request.value, timeout=10000)
        logger.info(f"Selected {request.value} in {request.selector}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Select error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/click")
async def click(request: ClickRequest):
    try:
        ctx = await get_context(request.session_id)
        await ctx["page"].click(request.selector, timeout=10000)
        logger.info(f"Clicked {request.selector}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Click error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hover")
async def hover(request: HoverRequest):
    try:
        ctx = await get_context(request.session_id)
        await ctx["page"].hover(request.selector, timeout=10000)
        logger.info(f"Hovered over {request.selector}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Hover error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/double_click")
async def double_click(request: ClickRequest):
    try:
        ctx = await get_context(request.session_id)
        await ctx["page"].dblclick(request.selector, timeout=10000)
        logger.info(f"Double clicked {request.selector}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Double click error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/drag")
async def drag(request: DragRequest):
    try:
        ctx = await get_context(request.session_id)
        source = await ctx["page"].query_selector(request.source)
        target = await ctx["page"].query_selector(request.target)
        
        if source and target:
            await source.drag_to(target, timeout=10000)
            logger.info(f"Dragged {request.source} to {request.target}")
            return {"success": True}
        else:
            raise HTTPException(status_code=400, detail="Elements not found")
    except Exception as e:
        logger.error(f"Drag error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scroll")
async def scroll(request: ScrollRequest):
    try:
        ctx = await get_context(request.session_id)
        if request.direction == "down":
            await ctx["page"].evaluate(f"window.scrollBy(0, {request.amount})")
        elif request.direction == "up":
            await ctx["page"].evaluate(f"window.scrollBy(0, -{request.amount})")
        elif request.direction == "left":
            await ctx["page"].evaluate(f"window.scrollBy(-{request.amount}, 0)")
        elif request.direction == "right":
            await ctx["page"].evaluate(f"window.scrollBy({request.amount}, 0)")
        logger.info(f"Scrolled {request.direction} by {request.amount}px")
        return {"success": True}
    except Exception as e:
        logger.error(f"Scroll error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit")
async def submit(request: ClickRequest):
    try:
        ctx = await get_context(request.session_id)
        await ctx["page"].click(request.selector, timeout=10000)
        logger.info(f"Submitted form at {request.selector}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Submit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify_text")
async def verify_text(request: dict):
    try:
        ctx = await get_context(request.session_id)
        text = await ctx["page"].inner_text()
        found = request["text"] in text
        logger.info(f"Verify text '{request['text']}': {found}")
        return {"found": found}
    except Exception as e:
        logger.error(f"Verify text error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify_element")
async def verify_element(request: dict):
    try:
        ctx = await get_context(request.session_id)
        element = await ctx["page"].query_selector(request["selector"])
        exists = element is not None
        if exists:
            visible = await element.is_visible()
        else:
            visible = False
        logger.info(f"Verify element '{request['selector']}': exists={exists}, visible={visible}")
        return {"exists": exists and visible}
    except Exception as e:
        logger.error(f"Verify element error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify_url")
async def verify_url(request: dict):
    try:
        ctx = await get_context(request.session_id)
        current_url = ctx["page"].url
        match = current_url == request["expected_url"]
        logger.info(f"Verify URL: expected={request['expected_url']}, actual={current_url}, match={match}")
        return {"match": match, "actual_url": current_url}
    except Exception as e:
        logger.error(f"Verify URL error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify_title")
async def verify_title(request: dict):
    try:
        ctx = await get_context(request.session_id)
        title = await ctx["page"].title()
        match = title == request["expected_title"]
        logger.info(f"Verify title: expected={request['expected_title']}, actual={title}, match={match}")
        return {"match": match, "actual_title": title}
    except Exception as e:
        logger.error(f"Verify title error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot")
async def screenshot(request: ScreenshotRequest):
    try:
        ctx = await get_context(request.session_id)
        timestamp = int(datetime.now().timestamp())
        screenshot_path = screenshots_dir / f"screenshot_{request.session_id}_{timestamp}.png"
        await ctx["page"].screenshot(path=str(screenshot_path), full_page=request.full_page)

        session_file = screenshots_dir / f"{request.session_id}_progress.json"
        progress = {}
        if session_file.exists():
            with open(session_file, 'r') as f:
                progress = json.load(f)

        progress["screenshots"] = progress.get("screenshots", [])
        progress["screenshots"].append({
            "timestamp": timestamp,
            "path": str(screenshot_path),
            "url": ctx["page"].url
        })

        with open(session_file, 'w') as f:
            json.dump(progress, f, indent=2, default=str)

        logger.info(f"Screenshot saved: {screenshot_path}")
        return {"success": True, "screenshot_path": str(screenshot_path), "timestamp": timestamp}
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot_base64")
async def screenshot_base64(request: ScreenshotRequest):
    try:
        ctx = await get_context(request.session_id)
        screenshot_bytes = await ctx["page"].screenshot(full_page=request.full_page)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        logger.info(f"Base64 screenshot captured for session {request.session_id}")
        return {"success": True, "screenshot": f"data:image/png;base64,{screenshot_b64}"}
    except Exception as e:
        logger.error(f"Base64 screenshot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/set_headful")
async def set_headful(request: SetHeadfulRequest):
    try:
        if request.session_id in contexts:
            contexts[request.session_id]["headful"] = request.headful
            session_configs[request.session_id]["headful"] = request.headful
            mode = "headful (visible)" if request.headful else "headless"
            logger.info(f"👁️  Session {request.session_id} set to {mode}")
            return {"success": True, "headful": request.headful}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Set headful error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_html")
async def get_html(request: GetHTMLRequest):
    try:
        ctx = await get_context(request.session_id)
        html_content = await ctx["page"].content()

        session_file = screenshots_dir / f"{request.session_id}_progress.json"
        progress = {}
        if session_file.exists():
            with open(session_file, 'r') as f:
                progress = json.load(f)

        progress["html_captures"] = progress.get("html_captures", [])
        progress["html_captures"].append({
            "timestamp": datetime.now().isoformat(),
            "url": ctx["page"].url,
            "html_length": len(html_content)
        })

        with open(session_file, 'w') as f:
            json.dump(progress, f, indent=2, default=str)

        logger.info(f"HTML captured for session {request.session_id} ({len(html_content)} chars)")
        return {"success": True, "html": html_content, "url": ctx["page"].url}
    except Exception as e:
        logger.error(f"Get HTML error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update_progress")
async def update_progress(request: ProgressUpdateRequest):
    try:
        session_file = screenshots_dir / f"{request.session_id}_progress.json"
        progress = {}
        if session_file.exists():
            with open(session_file, 'r') as f:
                progress = json.load(f)

        progress["steps"] = progress.get("steps", [])
        progress["steps"].append({
            "test_case_id": request.test_case_id,
            "step_number": request.step_number,
            "status": request.status,
            "message": request.message,
            "timestamp": datetime.now().isoformat()
        })

        progress["last_updated"] = datetime.now().isoformat()
        progress["total_steps"] = len(progress["steps"])

        with open(session_file, 'w') as f:
            json.dump(progress, f, indent=2, default=str)

        logger.info(f"Progress updated for session {request.session_id}: {request.message}")
        return {"success": True, "total_steps": progress["total_steps"]}
    except Exception as e:
        logger.error(f"Update progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/progress/{session_id}")
async def get_progress(session_id: str):
    try:
        session_file = screenshots_dir / f"{session_id}_progress.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                progress = json.load(f)
            return progress
        else:
            return {"message": "No progress data yet"}
    except Exception as e:
        logger.error(f"Get progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
