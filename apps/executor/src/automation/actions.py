"""
Browser Actions Module

Implements specific browser actions using Playwright.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes browser actions on a page."""
    
    def __init__(self, page):
        self.page = page
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL."""
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            logger.info(f"Navigated to {url}")
            return {"success": True, "url": url}
        except Exception as e:
            logger.error(f"Navigate error: {e}")
            return {"success": False, "error": str(e)}
    
    async def click(self, selector: str) -> Dict[str, Any]:
        """Click element."""
        try:
            await self.page.click(selector, timeout=10000)
            logger.info(f"Clicked {selector}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Click error: {e}")
            return {"success": False, "error": str(e)}
    
    async def fill(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill input field."""
        try:
            await self.page.fill(selector, value, timeout=10000)
            logger.info(f"Filled {selector} with {value}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Fill error: {e}")
            return {"success": False, "error": str(e)}
    
    async def drag(self, source: str, target: str) -> Dict[str, Any]:
        """Drag element from source to target."""
        try:
            source_el = await self.page.query_selector(source)
            target_el = await self.page.query_selector(target)
            
            if source_el and target_el:
                await source_el.drag_to(target_el, timeout=10000)
                logger.info(f"Dragged {source} to {target}")
                return {"success": True}
            else:
                return {"success": False, "error": "Elements not found"}
        except Exception as e:
            logger.error(f"Drag error: {e}")
            return {"success": False, "error": str(e)}
    
    async def hover(self, selector: str) -> Dict[str, Any]:
        """Hover over element."""
        try:
            await self.page.hover(selector, timeout=10000)
            logger.info(f"Hovered over {selector}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Hover error: {e}")
            return {"success": False, "error": str(e)}
    
    async def scroll(self, direction: str, amount: int) -> Dict[str, Any]:
        """Scroll page."""
        try:
            if direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await self.page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction == "left":
                await self.page.evaluate(f"window.scrollBy(-{amount}, 0)")
            elif direction == "right":
                await self.page.evaluate(f"window.scrollBy({amount}, 0)")
            logger.info(f"Scrolled {direction} by {amount}px")
            return {"success": True}
        except Exception as e:
            logger.error(f"Scroll error: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_text(self, text: str) -> Dict[str, Any]:
        """Verify text is present on page."""
        try:
            page_text = await self.page.inner_text()
            found = text in page_text
            logger.info(f"Verify text '{text}': {found}")
            return {"found": found}
        except Exception as e:
            logger.error(f"Verify text error: {e}")
            return {"found": False, "error": str(e)}
    
    async def verify_element(self, selector: str) -> Dict[str, Any]:
        """Verify element exists and is visible."""
        try:
            element = await self.page.query_selector(selector)
            exists = element is not None
            if exists:
                visible = await element.is_visible()
            else:
                visible = False
            logger.info(f"Verify element '{selector}': exists={exists}, visible={visible}")
            return {"exists": exists and visible}
        except Exception as e:
            logger.error(f"Verify element error: {e}")
            return {"exists": False, "error": str(e)}
