"""
Browser State Manager

Manages browser instances, contexts, and sessions
"""
import logging
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser state and contexts"""

    def __init__(self, screenshots_dir: Path):
        self.browsers = {}
        self.contexts = {}
        self.screenshots_dir = screenshots_dir
        self.session_configs = {}

    async def get_context(self, session_id: str, headful: bool = False):
        """Get or create browser context for session"""
        if session_id not in self.contexts:
            if "browser" not in self.browsers:
                browser_obj = await async_playwright().start()
                self.browsers["browser"] = browser_obj

            browser = self.browsers["browser"]
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"
            )
            page = await context.new_page()

            if headful:
                logger.info(f"👁️  Headful mode enabled for session {session_id}")

            self.contexts[session_id] = {
                "context": context,
                "page": page,
                "headful": headful
            }

            self.session_configs[session_id] = {
                "headful": headful,
                "created_at": datetime.now().isoformat(),
                "steps_completed": 0
            }

            logger.info(f"Created new context for session {session_id} (headful={headful})")

        return self.contexts[session_id]

    async def set_headful(self, session_id: str, headful: bool):
        """Set headful mode for session"""
        if session_id in self.contexts:
            self.contexts[session_id]["headful"] = headful
            self.session_configs[session_id]["headful"] = headful
            mode = "headful (visible)" if headful else "headless"
            logger.info(f"👁️  Session {session_id} set to {mode}")
            return True
        return False

    async def cleanup_session(self, session_id: str):
        """Cleanup browser context for session"""
        if session_id in self.contexts:
            context_data = self.contexts[session_id]
            await context_data["context"].close()
            del self.contexts[session_id]
            del self.session_configs[session_id]
            logger.info(f"Cleaned up session {session_id}")

    async def cleanup_all(self):
        """Cleanup all browser resources"""
        for context_data in self.contexts.values():
            await context_data["context"].close()

        for browser in self.browsers.values():
            await browser.close()

        self.contexts.clear()
        self.session_configs.clear()
        self.browsers.clear()
        logger.info("Cleaned up all browser resources")
