"""
Enhanced Orchestrator - Parallel Agent Execution with Async

Features:
- Async/await for better concurrency
- True parallel agent execution
- Dependency-aware task scheduling
- Resource-aware execution
- Merge point identification
"""
import asyncio
import logging
from typing import Dict, List, Callable, Set, Optional, Any
from datetime import datetime
from .base_agent import BaseAgent
from libs.task_manager.src.task_manager import get_task_manager


logger = logging.getLogger(__name__)


class EnhancedOrchestrator(BaseAgent):
    """Enhanced Orchestrator with async parallel execution"""

    def __init__(self, session_id: str, llm, agents: List[BaseAgent], max_parallel: int = 4):
        super().__init__(session_id, llm)
        self.agents = {agent.__class__.__name__: agent for agent in agents}
        self.max_parallel = max_parallel
        self.current_phase = "initial"
        self.task_manager = get_task_manager()
        self.merge_points: List[str] = []
        self.dependencies: Dict[str, Set[str]] = {}

    def get_system_prompt(self) -> str:
        return """You are Enhanced Master Orchestrator for automated QA testing.

AVAILABLE AGENTS:
- NavigationAgent: Handles page navigation and URL routing
- FormAgent: Fills and submits forms, validates inputs
- InteractionAgent: Handles clicks, drags, hover events
- VerificationAgent: Verifies expected results and states
- ReportAgent: Generates final test reports
- MergingAgent: Merges parallel agent results

PHASES:
1. PLANNING: Create test cases and execution plan
2. PREPARATION: Set up environments and contexts
3. PARALLEL_EXECUTION: Run independent tests in parallel
4. MERGE: Combine parallel results at merge points
5. VERIFICATION: Validate merged results
6. REPORTING: Generate comprehensive test report

PARALLEL EXECUTION RULES:
- Identify independent tasks (no dependencies)
- Execute independent tasks in parallel (up to max_parallel)
- Wait for merge points before proceeding
- Respect task dependencies
- Coordinate with MergingAgent at merge points

DEPENDENCY TRACKING:
- Track task dependencies: task_a -> task_b
- Wait for dependencies before execution
- Create merge points where parallel branches meet
- Merge results at merge points before continuing

OUTPUT FORMAT:
{
  "phase": "current_phase",
  "tasks": [
    {"task_id": "unique_id", "agent": "AgentName", "description": "...", "priority": 1, "dependencies": []}
  ],
  "merge_points": ["merge_point_1"],
  "parallel_groups": [["task1", "task2"], ["task3"]],
  "reasoning": "Why this coordination"
}"""

    def get_description(self) -> str:
        return "Enhanced Master Orchestrator - Parallel async agent coordination"

    async def orchestrate(
        self,
        url: str,
        domain_info: str,
        check_running: Callable[[], bool]
    ) -> bool:
        """Main orchestration loop with async/await"""

        logger.info(f"🎯 Enhanced Orchestrator starting QA test on {url}")
        logger.info(f"📊 Max parallel agents: {self.max_parallel}")

        context = {
            "url": url,
            "domain_info": domain_info,
            "phase": "planning",
            "test_cases": [],
            "current_test_case": None,
            "current_step": 0,
            "completed_tests": [],
            "failed_tests": [],
            "parallel_groups": [],
            "merge_points": []
        }

        max_iterations = 100
        iteration = 0

        # Start task monitoring
        await self.task_manager.start_monitoring()

        try:
            while check_running() and iteration < max_iterations:
                iteration += 1

                try:
                    # Get orchestration decision
                    decision = await asyncio.to_thread(self.think, context)
                    tasks = decision.get("tasks", [])
                    merge_points = decision.get("merge_points", [])
                    parallel_groups = decision.get("parallel_groups", [])

                    logger.info(
                        f"📋 Phase: {decision.get('phase')} - "
                        f"Tasks: {len(tasks)}, Groups: {len(parallel_groups)}, "
                        f"Merge Points: {len(merge_points)}"
                    )

                    # Execute parallel groups if present
                    if parallel_groups:
                        await self._execute_parallel_groups(parallel_groups, context)
                    # Execute tasks sequentially or in parallel
                    elif tasks:
                        await self._execute_tasks_with_parallel(tasks, context)

                    # Handle merge points
                    if merge_points:
                        await self._handle_merge_points(merge_points, context)

                    context["phase"] = decision.get("phase", "unknown")

                    if self._is_complete(context):
                        logger.info("✅ All tests completed successfully!")
                        return True

                    if iteration % 10 == 0:
                        stats = self.task_manager.get_stats()
                        logger.info(
                            f"📊 Status: {len(context['completed_tests'])} completed, "
                            f"{len(context['failed_tests'])} failed, "
                            f"Task Stats: {stats}"
                        )

                except Exception as e:
                    logger.error(f"Orchestration error: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

            logger.info(f"Orchestration finished after {iteration} iterations")
            return False

        finally:
            # Shutdown task manager
            await self.task_manager.shutdown()

    async def _execute_tasks_with_parallel(
        self,
        tasks: List[Dict],
        context: Dict
    ):
        """Execute tasks with parallel scheduling"""

        # Group independent tasks
        task_map = {task.get("task_id", ""): task for task in tasks}
        dependencies: Dict[str, Set[str]] = {}
        reverse_deps: Dict[str, Set[str]] = {}

        for task in tasks:
            task_id = task.get("task_id", "")
            deps = set(task.get("dependencies", []))
            dependencies[task_id] = deps

            for dep in deps:
                if dep not in reverse_deps:
                    reverse_deps[dep] = set()
                reverse_deps[dep].add(task_id)

        # Execute tasks respecting dependencies
        executed = set()
        pending = set(task_map.keys())

        while pending:
            # Find ready tasks (all dependencies satisfied)
            ready_tasks = [
                task_id
                for task_id in pending
                if dependencies[task_id].issubset(executed)
            ]

            if not ready_tasks:
                # Circular dependency or error
                logger.error("No ready tasks found - possible circular dependency")
                break

            # Execute ready tasks in parallel
            batch_size = min(len(ready_tasks), self.max_parallel)
            batch = ready_tasks[:batch_size]

            results = await asyncio.gather(
                *[self._run_agent_task_async(task_map[task_id], context)
                  for task_id in batch],
                return_exceptions=True
            )

            # Process results
            for task_id, result in zip(batch, results):
                if isinstance(result, Exception):
                    logger.error(f"Task {task_id} failed: {result}")
                    context["failed_tests"].append({
                        "task_id": task_id,
                        "error": str(result)
                    })
                else:
                    context["completed_tests"].append(result)

                executed.add(task_id)
                pending.discard(task_id)

    async def _execute_parallel_groups(
        self,
        groups: List[List[str]],
        context: Dict
    ):
        """Execute groups of parallel tasks sequentially"""

        for group in groups:
            logger.info(f"🚀 Executing parallel group: {len(group)} tasks")

            # Create tasks from group
            tasks = []
            for task_id in group:
                task = next(
                    (t for t in context.get("tasks", []) if t.get("task_id") == task_id),
                    None
                )
                if task:
                    tasks.append(self._run_agent_task_async(task, context))

            # Execute group in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for task_id, result in zip(group, results):
                if isinstance(result, Exception):
                    logger.error(f"Group task {task_id} failed: {result}")
                    context["failed_tests"].append({
                        "task_id": task_id,
                        "error": str(result)
                    })
                else:
                    context["completed_tests"].append(result)

    async def _run_agent_task_async(
        self,
        task: Dict,
        context: Dict
    ) -> Dict:
        """Run a single agent task asynchronously"""

        task_id = task.get("task_id", "unknown")
        agent_name = task.get("agent")
        task_desc = task.get("task", "")

        if agent_name not in self.agents:
            logger.error(f"Unknown agent: {agent_name}")
            return {"agent": agent_name, "success": False, "error": "Agent not found"}

        agent = self.agents[agent_name]
        agent_context = {
            **context,
            "task_description": task_desc,
            "task_id": task_id
        }

        try:
            # Run agent thinking and execution
            action = await asyncio.to_thread(agent.think, agent_context)
            result = await asyncio.to_thread(agent.execute, action)
            agent.learn(action, result)

            return {
                "agent": agent_name,
                "task": task_desc,
                "success": True,
                "result": str(result)[:200],
                "task_id": task_id
            }

        except Exception as e:
            logger.error(f"Agent {agent_name} task {task_id} error: {e}")
            import traceback
            traceback.print_exc()

            return {
                "agent": agent_name,
                "task": task_desc,
                "success": False,
                "error": str(e),
                "task_id": task_id
            }

    async def _handle_merge_points(
        self,
        merge_points: List[str],
        context: Dict
    ):
        """Handle merge points for parallel execution"""

        for merge_point in merge_points:
            logger.info(f"🔀 Handling merge point: {merge_point}")

            if "MergingAgent" in self.agents:
                merging_agent = self.agents["MergingAgent"]

                # Collect results from completed tests
                for test in context.get("completed_tests", []):
                    agent_name = test.get("agent")
                    result = {
                        "task_id": test.get("task_id"),
                        "result": test.get("result"),
                        "success": test.get("success")
                    }

                    # Use asyncio.to_thread for blocking call
                    await asyncio.to_thread(
                        merging_agent.collect_agent_results,
                        agent_name,
                        result
                    )

                # Merge results
                merge_result = await asyncio.to_thread(merging_agent.merge_results)
                logger.info(f"Merge completed: {merge_point}")

                # Update context with merged results
                context["merged_results"] = merge_result

            else:
                logger.warning("MergingAgent not found, skipping merge point")

    def _is_complete(self, context: Dict) -> bool:
        """Check if all tests complete"""

        return context.get("phase") == "reporting" and len(context.get("completed_tests", [])) > 0


# Backwards compatibility - use EnhancedOrchestrator
OrchestratorAgent = EnhancedOrchestrator
