"""
Background Task Manager - Safe resource management for async operations

Manages background tasks with:
- Safe cleanup on completion/failure
- Resource tracking (browsers, memory)
- Health monitoring
- Graceful shutdown
"""
import asyncio
import logging
import threading
import psutil
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task lifecycle status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TaskResource:
    """Track task resources"""
    task_id: str
    browser_contexts: List[str] = field(default_factory=list)
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class BackgroundTask:
    """Background task metadata"""
    task_id: str
    name: str
    coro: Callable
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[Exception] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resource: TaskResource = field(default_factory=TaskResource)
    cleanup_handlers: List[Callable] = field(default_factory=list)


class TaskManager:
    """
    Manages background tasks with safe resource cleanup

    Features:
    - Async task execution
    - Resource tracking
    - Health monitoring
    - Graceful shutdown
    - Automatic cleanup
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        self.tasks: Dict[str, BackgroundTask] = {}
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks = 0
        self._lock = asyncio.Lock()
        self._monitor_interval = 5.0
        self._shutdown_requested = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def create_task(
        self,
        name: str,
        coro: Callable,
        cleanup_handlers: Optional[List[Callable]] = None,
        timeout: Optional[float] = None
    ) -> str:
        """Create and start a new background task"""

        task_id = str(uuid.uuid4())

        task = BackgroundTask(
            task_id=task_id,
            name=name,
            coro=coro,
            status=TaskStatus.PENDING,
            resource=TaskResource(task_id=task_id)
        )

        if cleanup_handlers:
            task.cleanup_handlers.extend(cleanup_handlers)

        self.tasks[task_id] = task
        logger.info(f"Created task {name} (id: {task_id})")

        # Start task execution
        asyncio.create_task(self._execute_task(task, timeout))

        return task_id

    async def _execute_task(
        self,
        task: BackgroundTask,
        timeout: Optional[float] = None
    ):
        """Execute task with timeout and resource tracking"""

        async with self._lock:
            if self.running_tasks >= self.max_concurrent_tasks:
                task.status = TaskStatus.FAILED
                task.error = Exception("Max concurrent tasks reached")
                logger.error(f"Task {task.name} failed: max concurrency reached")
                return

            self.running_tasks += 1
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task.resource.last_activity = datetime.now()

        try:
            # Execute with timeout if specified
            if timeout:
                result = await asyncio.wait_for(task.coro(), timeout=timeout)
            else:
                result = await task.coro()

            task.result = result
            task.status = TaskStatus.COMPLETED

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error = Exception(f"Task timeout after {timeout}s")
            logger.error(f"Task {task.name} timed out")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = e
            logger.error(f"Task {task.name} failed: {e}")

        finally:
            async with self._lock:
                self.running_tasks -= 1

            task.completed_at = datetime.now()
            task.resource.last_activity = datetime.now()

            # Run cleanup handlers
            await self._cleanup_task(task)

    async def _cleanup_task(self, task: BackgroundTask):
        """Run cleanup handlers for task"""

        for handler in task.cleanup_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(task)
                else:
                    handler(task)
            except Exception as e:
                logger.error(f"Cleanup handler error for task {task.name}: {e}")

        logger.info(f"Cleaned up task {task.name} (id: {task.task_id})")

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""

        task = self.tasks.get(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found")
            return False

        if task.status != TaskStatus.RUNNING:
            logger.warning(f"Task {task_id} is not running")
            return False

        task.status = TaskStatus.CANCELLED
        task.error = Exception("Task cancelled by user")
        logger.info(f"Cancelled task {task.name} (id: {task_id})")

        return True

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""

        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": str(task.error) if task.error else None,
            "resource": {
                "browser_contexts": task.resource.browser_contexts,
                "memory_usage_mb": task.resource.memory_usage_mb,
                "cpu_usage_percent": task.resource.cpu_usage_percent,
                "last_activity": task.resource.last_activity.isoformat()
            }
        }

    def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status"""

        tasks = []

        for task in self.tasks.values():
            if status_filter and task.status != status_filter:
                continue

            tasks.append(self.get_task_status(task.task_id))

        return tasks

    async def update_resource_usage(self, task_id: str):
        """Update resource usage for a task"""

        task = self.tasks.get(task_id)
        if not task:
            return

        process = psutil.Process()

        try:
            task.resource.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            task.resource.cpu_usage_percent = process.cpu_percent()
            task.resource.last_activity = datetime.now()
        except Exception as e:
            logger.error(f"Failed to update resource usage: {e}")

    async def start_monitoring(self):
        """Start background monitoring of tasks"""

        if self._monitor_task and not self._monitor_task.done():
            logger.warning("Monitor already running")
            return

        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Started task monitoring")

    async def stop_monitoring(self):
        """Stop background monitoring"""

        self._shutdown_requested = True

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped task monitoring")

    async def _monitor_loop(self):
        """Monitor tasks and cleanup stale ones"""

        while not self._shutdown_requested:
            try:
                await asyncio.sleep(self._monitor_interval)

                # Update resource usage for running tasks
                for task_id, task in self.tasks.items():
                    if task.status == TaskStatus.RUNNING:
                        await self.update_resource_usage(task_id)

                # Clean up completed tasks older than 1 hour
                self._cleanup_stale_tasks()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")

    def _cleanup_stale_tasks(self):
        """Remove stale tasks from memory"""

        stale_threshold = datetime.now().timestamp() - 3600  # 1 hour

        stale_tasks = [
            task_id
            for task_id, task in self.tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            and task.completed_at
            and task.completed_at.timestamp() < stale_threshold
        ]

        for task_id in stale_tasks:
            del self.tasks[task_id]
            logger.info(f"Removed stale task {task_id}")

    async def shutdown(self):
        """Gracefully shutdown all tasks"""

        logger.info("Shutting down task manager...")

        # Cancel all running tasks
        for task in self.tasks.values():
            if task.status == TaskStatus.RUNNING:
                self.cancel_task(task.task_id)

        # Stop monitoring
        await self.stop_monitoring()

        # Cleanup all tasks
        for task in list(self.tasks.values()):
            await self._cleanup_task(task)

        self.tasks.clear()
        logger.info("Task manager shutdown complete")

    def register_browser_context(self, task_id: str, context_id: str):
        """Register a browser context for a task"""

        task = self.tasks.get(task_id)
        if task:
            task.resource.browser_contexts.append(context_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get task manager statistics"""

        status_counts = {}

        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_tasks": len(self.tasks),
            "running_tasks": self.running_tasks,
            "max_concurrent": self.max_concurrent_tasks,
            "status_counts": status_counts
        }


# Global task manager instance
_global_task_manager: Optional[TaskManager] = None


def get_task_manager(max_concurrent: int = 10) -> TaskManager:
    """Get or create global task manager"""

    global _global_task_manager

    if _global_task_manager is None:
        _global_task_manager = TaskManager(max_concurrent_tasks=max_concurrent)

    return _global_task_manager
