"""
Browser Management Module

Manages Playwright browser instances and contexts.
"""
import asyncio
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser instances for multiple sessions."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.contexts = {}
    
    async def initialize(self):
        """Initialize Playwright browser."""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage"]
            )
            logger.info("Browser initialized")
    
    async def get_context(self, session_id: str):
        """Get or create context for session."""
        if session_id not in self.contexts:
            await self.initialize()
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            self.contexts[session_id] = {"context": context, "page": page}
            logger.info(f"Created context for session {session_id}")
        
        return self.contexts[session_id]
    
    async def close_context(self, session_id: str):
        """Close context for session."""
        if session_id in self.contexts:
            await self.contexts[session_id]["context"].close()
            del self.contexts[session_id]
            logger.info(f"Closed context for session {session_id}")
    
    async def close_all(self):
        """Close all contexts and browser."""
        for session_id in list(self.contexts.keys()):
            await self.close_context(session_id)
        
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser manager closed all")


# Global browser manager
browser_manager = BrowserManager()
