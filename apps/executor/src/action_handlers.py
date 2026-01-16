"""
Browser Action Handlers

Executes specific browser actions (navigate, click, fill, etc.)
"""
import base64
import json
import logging
from datetime import datetime
from fastapi import HTTPException
from apps.executor.src.requests import (
    NavigateRequest, FillRequest, SelectRequest,
    ClickRequest, HoverRequest, DragRequest, ScrollRequest,
    ScreenshotRequest, SetHeadfulRequest, GetHTMLRequest,
    ProgressUpdateRequest
)


logger = logging.getLogger(__name__)


class ActionHandlers:
    """Handles browser action execution"""

    def __init__(self, browser_manager, screenshots_dir, minio_client=None):
        self.browser_manager = browser_manager
        self.screenshots_dir = screenshots_dir
        self.minio_client = minio_client

    async def navigate(self, request: NavigateRequest):
        """Navigate to URL"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            await ctx["page"].goto(request.url, wait_until="networkidle", timeout=30000)
            logger.info(f"Navigated to {request.url}")
            return {"success": True, "url": request.url}
        except Exception as e:
            logger.error(f"Navigate error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def fill(self, request: FillRequest):
        """Fill form field"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            await ctx["page"].fill(request.selector, request.value, timeout=10000)
            logger.info(f"Filled {request.selector} with {request.value}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Fill error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def select_option(self, request: SelectRequest):
        """Select dropdown option"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            await ctx["page"].select_option(request.selector, request.value, timeout=10000)
            logger.info(f"Selected {request.value} in {request.selector}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Select error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def click(self, request: ClickRequest):
        """Click element"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            await ctx["page"].click(request.selector, timeout=10000)
            logger.info(f"Clicked {request.selector}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Click error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def hover(self, request: HoverRequest):
        """Hover over element"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            await ctx["page"].hover(request.selector, timeout=10000)
            logger.info(f"Hovered over {request.selector}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Hover error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def double_click(self, request: ClickRequest):
        """Double click element"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            await ctx["page"].dblclick(request.selector, timeout=10000)
            logger.info(f"Double clicked {request.selector}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Double click error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def drag(self, request: DragRequest):
        """Drag element to target"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
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

    async def scroll(self, request: ScrollRequest):
        """Scroll page"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
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

    async def submit(self, request: ClickRequest):
        """Submit form"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            await ctx["page"].click(request.selector, timeout=10000)
            logger.info(f"Submitted form at {request.selector}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Submit error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_text(self, session_id: str, text: str):
        """Verify text present on page"""
        try:
            ctx = await self.browser_manager.get_context(session_id)
            text_content = await ctx["page"].inner_text()
            found = text in text_content
            logger.info(f"Verify text '{text}': {found}")
            return {"found": found}
        except Exception as e:
            logger.error(f"Verify text error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_element(self, session_id: str, selector: str):
        """Verify element exists and is visible"""
        try:
            ctx = await self.browser_manager.get_context(session_id)
            element = await ctx["page"].query_selector(selector)
            exists = element is not None
            if exists:
                visible = await element.is_visible()
            else:
                visible = False
            logger.info(f"Verify element '{selector}': exists={exists}, visible={visible}")
            return {"exists": exists and visible}
        except Exception as e:
            logger.error(f"Verify element error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_url(self, session_id: str, expected_url: str):
        """Verify current URL"""
        try:
            ctx = await self.browser_manager.get_context(session_id)
            current_url = ctx["page"].url
            match = current_url == expected_url
            logger.info(f"Verify URL: expected={expected_url}, actual={current_url}, match={match}")
            return {"match": match, "actual_url": current_url}
        except Exception as e:
            logger.error(f"Verify URL error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_title(self, session_id: str, expected_title: str):
        """Verify page title"""
        try:
            ctx = await self.browser_manager.get_context(session_id)
            title = await ctx["page"].title()
            match = title == expected_title
            logger.info(f"Verify title: expected={expected_title}, actual={title}, match={match}")
            return {"match": match, "actual_title": title}
        except Exception as e:
            logger.error(f"Verify title error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def screenshot(self, request: ScreenshotRequest):
        """Take screenshot and save to MinIO or file"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            timestamp = int(datetime.now().timestamp())
            screenshot_bytes = await ctx["page"].screenshot(full_page=request.full_page)

            if self.minio_client:
                screenshot_url = self.minio_client.upload_screenshot(
                    request.session_id,
                    screenshot_bytes,
                    request.full_page
                )
                screenshot_path = screenshot_url or str(self.screenshots_dir / f"screenshot_{request.session_id}_{timestamp}.png")
                if screenshot_url and screenshot_url.startswith("http"):
                    with open(self.screenshots_dir / f"screenshot_{request.session_id}_{timestamp}.png", 'wb') as f:
                        f.write(screenshot_bytes)
            else:
                screenshot_path = self.screenshots_dir / f"screenshot_{request.session_id}_{timestamp}.png"
                with open(screenshot_path, 'wb') as f:
                    f.write(screenshot_bytes)
                screenshot_url = None

            session_file = self.screenshots_dir / f"{request.session_id}_progress.json"
            progress = {}
            if session_file.exists():
                with open(session_file, 'r') as f:
                    progress = json.load(f)

            progress["screenshots"] = progress.get("screenshots", [])
            progress["screenshots"].append({
                "timestamp": timestamp,
                "path": str(screenshot_path),
                "url": screenshot_url or str(screenshot_path),
                "page_url": ctx["page"].url
            })

            with open(session_file, 'w') as f:
                json.dump(progress, f, indent=2, default=str)

            logger.info(f"Screenshot saved: {screenshot_path}")
            return {"success": True, "screenshot_path": str(screenshot_path), "timestamp": timestamp, "url": screenshot_url}
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def screenshot_base64(self, request: ScreenshotRequest):
        """Take screenshot and return as base64"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            screenshot_bytes = await ctx["page"].screenshot(full_page=request.full_page)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            logger.info(f"Base64 screenshot captured for session {request.session_id}")
            return {"success": True, "screenshot": f"data:image/png;base64,{screenshot_b64}"}
        except Exception as e:
            logger.error(f"Base64 screenshot error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def set_headful(self, request: SetHeadfulRequest):
        """Toggle headful mode"""
        try:
            success = await self.browser_manager.set_headful(request.session_id, request.headful)
            if success:
                return {"success": True, "headful": request.headful}
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        except Exception as e:
            logger.error(f"Set headful error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_html(self, request: GetHTMLRequest):
        """Get HTML content"""
        try:
            ctx = await self.browser_manager.get_context(request.session_id)
            html_content = await ctx["page"].content()

            session_file = self.screenshots_dir / f"{request.session_id}_progress.json"
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

    async def update_progress(self, request: ProgressUpdateRequest):
        """Update progress tracking"""
        try:
            session_file = self.screenshots_dir / f"{request.session_id}_progress.json"
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
