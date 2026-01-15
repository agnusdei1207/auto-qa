"""
Orchestrator Agent - Master Coordinator
"""
import json
import logging
from typing import Dict, List, Callable
from .base_agent import BaseAgent


logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Master Orchestrator - Coordinates all QA testing agents"""
    
    def __init__(self, session_id: str, llm, agents: List[BaseAgent]):
        super().__init__(session_id, llm)
        self.agents = {agent.__class__.__name__: agent for agent in agents}
        self.current_phase = "initial"
        self.test_cases = []
    
    def get_system_prompt(self) -> str:
        return """You are Master Orchestrator for automated QA testing.

AVAILABLE AGENTS:
- NavigationAgent: Handles page navigation and URL routing
- FormAgent: Fills and submits forms, validates inputs
- InteractionAgent: Handles clicks, drags, hover events
- VerificationAgent: Verifies expected results and states
- ReportAgent: Generates final test reports

PHASES:
1. PLANNING: Create test cases from domain information
2. EXECUTION: Run test cases with appropriate agents
3. VERIFICATION: Validate test results
4. REPORTING: Generate comprehensive test report

COORDINATION RULES:
- Start by analyzing domain info and creating test cases
- Delegate to specialized agents for each test step
- Use NavigationAgent for page navigation
- Use FormAgent for form-related operations
- Use InteractionAgent for UI interactions
- Use VerificationAgent to check results
- Generate report after all tests complete

OUTPUT FORMAT:
{
  "phase": "current_phase",
  "agent_tasks": [
    {"agent": "AgentName", "task": "description", "priority": 1}
  ],
  "reasoning": "Why this coordination"
}"""
    
    def get_description(self) -> str:
        return "Master Orchestrator - Coordinates all QA testing agents"
    
    def orchestrate(self, url: str, domain_info: str, check_running: Callable[[], bool]) -> bool:
        """Main orchestration loop"""
        logger.info(f"🎯 Orchestrator starting QA test on {url}")
        
        context = {
            "url": url,
            "domain_info": domain_info,
            "phase": "planning",
            "test_cases": [],
            "current_test_case": None,
            "current_step": 0,
            "completed_tests": [],
            "failed_tests": []
        }
        
        max_iterations = 100
        iteration = 0
        
        while check_running() and iteration < max_iterations:
            iteration += 1
            
            try:
                decision = self.think(context)
                agent_tasks = decision.get("agent_tasks", [])
                
                logger.info(f"📋 Phase: {decision.get('phase')} - Tasks: {len(agent_tasks)}")
                
                self._execute_tasks(agent_tasks, context)
                context["phase"] = decision.get('phase', 'unknown')
                
                if self._is_complete(context):
                    logger.info("✅ All tests completed successfully!")
                    return True
                
                if iteration % 10 == 0:
                    logger.info(f"📊 Status: {len(context['completed_tests'])} completed, {len(context['failed_tests'])} failed")
            
            except Exception as e:
                logger.error(f"Orchestration error: {e}")
                continue
        
        logger.info(f"Orchestration finished after {iteration} iterations")
        return False
    
    def _execute_tasks(self, tasks: List[Dict], context: Dict):
        """Execute agent tasks"""
        for task in sorted(tasks, key=lambda t: t.get("priority", 0)):
            agent_name = task.get("agent")
            if agent_name in self.agents:
                result = self._run_agent_task(
                    self.agents[agent_name],
                    task,
                    context
                )
                if result.get("success"):
                    context["completed_tests"].append(result)
                else:
                    context["failed_tests"].append(result)
    
    def _run_agent_task(self, agent: BaseAgent, task: Dict, context: Dict) -> Dict:
        """Run a single agent task"""
        task_desc = task.get("task", "")
        agent_context = {
            **context,
            "task_description": task_desc
        }
        
        try:
            action = agent.think(agent_context)
            result = agent.execute(action)
            agent.learn(action, result)
            
            return {
                "agent": agent.__class__.__name__,
                "task": task_desc,
                "success": True,
                "result": result[:200]
            }
        except Exception as e:
            logger.error(f"Agent {agent.__class__.__name__} error: {e}")
            return {"agent": agent.__class__.__name__, "success": False, "error": str(e)}
    
    def _is_complete(self, context: Dict) -> bool:
        """Check if all tests complete"""
        return context.get("phase") == "reporting" and len(context.get("completed_tests", [])) > 0
