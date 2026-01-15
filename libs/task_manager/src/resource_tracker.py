"""
Task Resource Tracker

Tracks task resources (memory, CPU, browsers)
"""
import logging
from datetime import datetime
from typing import List


logger = logging.getLogger(__name__)


class TaskResource:
    """Track task resources"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.browser_contexts: List[str] = []
        self.memory_usage_mb: float = 0.0
        self.cpu_usage_percent: float = 0.0
        self.created_at: datetime = datetime.now()
        self.last_activity: datetime = datetime.now()

    def add_browser_context(self, context_id: str):
        """Add browser context to tracking"""
        if context_id not in self.browser_contexts:
            self.browser_contexts.append(context_id)
            logger.info(f"Added browser context {context_id} to task {self.task_id}")

    def remove_browser_context(self, context_id: str):
        """Remove browser context from tracking"""
        if context_id in self.browser_contexts:
            self.browser_contexts.remove(context_id)
            logger.info(f"Removed browser context {context_id} from task {self.task_id}")

    def update_resource_usage(self, memory_mb: float, cpu_percent: float):
        """Update resource usage metrics"""
        self.memory_usage_mb = memory_mb
        self.cpu_usage_percent = cpu_percent
        self.last_activity = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "task_id": self.task_id,
            "browser_contexts": self.browser_contexts,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }
