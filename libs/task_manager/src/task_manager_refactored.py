"""
Background Task Manager - Refactored with separated modules

Manages background tasks with:
- Safe cleanup on completion/failure
- Resource tracking (browsers, memory)
- Health monitoring
- Graceful shutdown

Components:
- task_metadata.py: Task lifecycle and status
- resource_tracker.py: Resource usage tracking
"""
import asyncio
import logging
import psutil
from typing import Dict, Any, Optional, Callable, List

from libs.task_manager.src.task_metadata import BackgroundTask, TaskStatus
from libs.task_manager.src.resource_tracker import TaskResource


logger = logging.getLogger(__name__)


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
        self._resources: Dict[str, TaskResource] = {}

    async def create_task(
        self,
        name: str,
        coro: Callable,
        cleanup_handlers: Optional[List[Callable]] = None,
        timeout: Optional[float] = None
    ) -> str:
        """Create and start a new background task"""

        task = BackgroundTask(
            name=name,
            coro=coro,
            cleanup_handlers=cleanup_handlers
        )

        # Create resource tracker
        self._resources[task.task_id] = TaskResource(task.task_id)

        self.tasks[task.task_id] = task
        logger.info(f"Created task {name} (id: {task.task_id})")

        # Start task execution
        asyncio.create_task(self._execute_task(task, timeout))

        return task.task_id

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
            task.start()
            self._resources[task.task_id].last_activity = task.started_at

        try:
            # Execute with timeout if specified
            if timeout:
                result = await asyncio.wait_for(task.coro(), timeout=timeout)
            else:
                result = await task.coro()

            task.complete(result)

        except asyncio.TimeoutError:
            task.timeout(Exception(f"Task timeout after {timeout}s"))
            logger.error(f"Task {task.name} timed out")

        except Exception as e:
            task.fail(e)

        finally:
            async with self._lock:
                self.running_tasks -= 1

            task.completed_at = task.completed_at or asyncio.get_event_loop().time()
            self._resources[task.task_id].last_activity = task.completed_at

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

        task.cancel()
        logger.info(f"Cancelled task {task.name} (id: {task_id})")

        return True

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""

        task = self.tasks.get(task_id)
        if not task:
            return None

        resource = self._resources.get(task_id)
        resource_data = resource.to_dict() if resource else {}

        return {
            "task": task.to_dict(),
            "resource": resource_data
        }

    def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status"""

        tasks = []

        for task in self.tasks.values():
            if status_filter and task.status != status_filter:
                continue

            task_data = self.get_task_status(task.task_id)
            if task_data:
                tasks.append(task_data)

        return tasks

    async def update_resource_usage(self, task_id: str):
        """Update resource usage for a task"""

        task = self.tasks.get(task_id)
        resource = self._resources.get(task_id)
        if not task or not resource:
            return

        process = psutil.Process()

        try:
            resource.update_resource_usage(
                process.memory_info().rss / 1024 / 1024,
                process.cpu_percent()
            )
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

        stale_threshold = asyncio.get_event_loop().time() - 3600  # 1 hour

        stale_tasks = [
            task_id
            for task_id, task in self.tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            and task.completed_at
            and task.completed_at.timestamp() if hasattr(task.completed_at, 'timestamp') else task.completed_at < stale_threshold
        ]

        for task_id in stale_tasks:
            del self.tasks[task_id]
            if task_id in self._resources:
                del self._resources[task_id]
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
        self._resources.clear()
        logger.info("Task manager shutdown complete")

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
            "status_counts": status_counts,
            "active_resources": len(self._resources)
        }


# Global task manager instance
_global_task_manager: Optional[TaskManager] = None


def get_task_manager(max_concurrent: int = 10) -> TaskManager:
    """Get or create global task manager"""

    global _global_task_manager

    if _global_task_manager is None:
        _global_task_manager = TaskManager(max_concurrent_tasks=max_concurrent)

    return _global_task_manager
