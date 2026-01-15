"""
Task Metadata

Task lifecycle and status tracking
"""
import uuid
import logging
from datetime import datetime
from typing import Callable, Optional, Any, List
from enum import Enum


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task lifecycle status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class BackgroundTask:
    """Background task metadata"""

    def __init__(
        self,
        name: str,
        coro: Callable,
        task_id: Optional[str] = None,
        cleanup_handlers: Optional[List[Callable]] = None
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.name = name
        self.coro = coro
        self.status = TaskStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[Exception] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.cleanup_handlers = cleanup_handlers or []

    def start(self):
        """Mark task as started"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        logger.info(f"Task {self.name} (id: {self.task_id}) started")

    def complete(self, result: Any = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
        logger.info(f"Task {self.name} (id: {self.task_id}) completed")

    def fail(self, error: Exception):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
        logger.error(f"Task {self.name} (id: {self.task_id}) failed: {error}")

    def cancel(self):
        """Mark task as cancelled"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
        logger.info(f"Task {self.name} (id: {self.task_id}) cancelled")

    def timeout(self, error: Exception):
        """Mark task as timed out"""
        self.status = TaskStatus.TIMEOUT
        self.error = error
        self.completed_at = datetime.now()
        logger.error(f"Task {self.name} (id: {self.task_id}) timed out")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": str(self.error) if self.error else None,
            "result": str(self.result)[:200] if self.result else None
        }
