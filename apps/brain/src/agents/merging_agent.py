"""
Merging Agent - Combine Parallel Results

Merges results from multiple parallel agents,
resolves conflicts, and creates unified report.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent
from libs.database.src.error_logger import ErrorLogger, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class MergingAgent(BaseAgent):
    """Merges results from parallel agent execution"""

    def __init__(self, session_id: str, llm, error_logger: ErrorLogger):
        super().__init__(session_id, llm)
        self.error_logger = error_logger
        self.agent_results = {}
        self.conflicts = []
        self.merged_results = {}

    def get_system_prompt(self) -> str:
        return """You are Merging Agent for web automation testing.

Your role is to:
1. Collect results from all parallel agents
2. Identify and resolve conflicts
3. Merge results into unified dataset
4. Generate final comprehensive report
5. Log all merging decisions

OUTPUT FORMAT:
{
  "action": "collect_results|resolve_conflict|merge_results|generate_final_report",
  "agent": "agent name",
  "results": "agent results",
  "conflict_type": "type of conflict",
  "resolution": "how to resolve",
  "priority": 1
}"""

    def get_description(self) -> str:
        return "Merging Agent - Combines parallel agent results"

    def collect_agent_results(self, agent_name: str, results: Dict[str, Any]):
        """Collect results from an agent"""
        self.agent_results[agent_name] = {
            "results": results,
            "collected_at": datetime.now().isoformat(),
            "status": "collected"
        }
        logger.info(f"Collected results from {agent_name}")

    def resolve_conflicts(
        self,
        conflict_type: str,
        agent1: str,
        agent2: str,
        details: str
    ):
        """Identify and log conflicts between agents"""
        conflict = {
            "conflict_id": self._generate_conflict_id(),
            "timestamp": datetime.now().isoformat(),
            "conflict_type": conflict_type,
            "agents": [agent1, agent2],
            "details": details,
            "resolution": None,
            "resolved_by": None
        }

        self.conflicts.append(conflict)

        self.error_logger.log_error(
            error=Exception(f"Agent conflict: {conflict_type}"),
            agent="MergingAgent",
            action="resolve_conflicts",
            category=ErrorCategory.LOGIC,
            severity=ErrorSeverity.MEDIUM,
            context={
                "agents_involved": [agent1, agent2],
                "conflict_details": details
            }
        )

        logger.warning(f"Conflict detected: {conflict_type} between {agent1} and {agent2}")

    def merge_results(self) -> Dict[str, Any]:
        """Merge all agent results into unified dataset"""
        self.merged_results = {
            "session_id": self.session_id,
            "merged_at": datetime.now().isoformat(),
            "agents_participated": list(self.agent_results.keys()),
            "total_agents": len(self.agent_results),
            "merged_data": {},
            "conflicts_resolved": len([c for c in self.conflicts if c["resolution"]]),
            "total_conflicts": len(self.conflicts)
        }

        for agent_name, agent_data in self.agent_results.items():
            results = agent_data["results"]

            for key, value in results.items():
                if key not in self.merged_results["merged_data"]:
                    self.merged_results["merged_data"][key] = []

                if isinstance(value, list):
                    self.merged_results["merged_data"][key].extend(value)
                elif isinstance(value, dict):
                    if key not in self.merged_results["merged_data"] or not isinstance(self.merged_results["merged_data"][key], dict):
                        self.merged_results["merged_data"][key] = {}
                    self.merged_results["merged_data"][key].update(value)
                else:
                    self.merged_results["merged_data"][key] = value

        logger.info(f"Merged results from {len(self.agent_results)} agents")
        return self.merged_results

    def prioritize_results(self, priority_order: List[str]) -> Dict[str, Any]:
        """Prioritize results based on agent priority"""
        prioritized = {
            "session_id": self.session_id,
            "prioritized_at": datetime.now().isoformat(),
            "priority_order": priority_order,
            "final_results": {}
        }

        for agent in priority_order:
            if agent in self.agent_results:
                prioritized["final_results"][agent] = self.agent_results[agent]["results"]

        for agent in self.agent_results:
            if agent not in priority_order:
                prioritized["final_results"][agent] = self.agent_results[agent]["results"]

        return prioritized

    def validate_merged_results(self) -> List[str]:
        """Validate merged results for consistency"""
        validation_issues = []

        merged = self.merged_results.get("merged_data", {})

        if not merged:
            validation_issues.append("No merged data available")
            return validation_issues

        if "test_cases" in merged:
            total_tests = merged.get("total_tests", 0)
            completed_tests = len([tc for tc in merged["test_cases"] if tc.get("status") == "completed"])

            if completed_tests > total_tests:
                validation_issues.append(f"Completed tests ({completed_tests}) exceed total tests ({total_tests})")

        if "actions" in merged:
            for action in merged["actions"]:
                if not action.get("action_type"):
                    validation_issues.append(f"Action missing action_type: {action}")

        if "conflicts" in merged and merged["conflicts"]:
            unresolved = [c for c in merged["conflicts"] if not c.get("resolution")]
            if unresolved:
                validation_issues.append(f"{len(unresolved)} conflicts remain unresolved")

        return validation_issues

    def generate_final_report(self) -> str:
        """Generate final comprehensive merged report"""
        report = {
            "session_id": self.session_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_agents": len(self.agent_results),
                "total_conflicts": len(self.conflicts),
                "resolved_conflicts": len([c for c in self.conflicts if c["resolution"]]),
                "validation_issues": len(self.validate_merged_results())
            },
            "agent_results": self.agent_results,
            "conflicts": self.conflicts,
            "merged_results": self.merged_results
        }

        return self._format_report(report)

    def _generate_conflict_id(self) -> str:
        """Generate unique conflict ID"""
        import uuid
        return f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

    def _format_report(self, report: Dict[str, Any]) -> str:
        """Format final merged report"""
        summary = report["summary"]

        formatted = f"""
{'=' * 70}
MERGED RESULTS REPORT - Session {self.session_id}
{'=' * 70}

📊 Summary
{'=' * 70}
Total Agents Participating: {summary['total_agents']}
Total Conflicts: {summary['total_conflicts']}
Resolved Conflicts: {summary['resolved_conflicts']}
Unresolved Conflicts: {summary['total_conflicts'] - summary['resolved_conflicts']}
Validation Issues: {summary['validation_issues']}

Generated At: {report['generated_at'][:19]}

{'=' * 70}
🤖 Agent Results
{'=' * 70}
"""

        for agent, data in report["agent_results"].items():
            formatted += f"""
[Agent: {agent}]
  Collected At: {data['collected_at'][:19]}
  Status: {data['status']}
  Results Keys: {list(data['results'].keys())}
"""

        if report["conflicts"]:
            formatted += f"\n{'=' * 70}\n⚠️  CONFLICTS DETECTED\n{'=' * 70}\n"
            for conflict in report["conflicts"][:10]:
                formatted += f"""
[Conflict ID: {conflict['conflict_id']}]
  Type: {conflict['conflict_type']}
  Agents: {', '.join(conflict['agents'])}
  Details: {conflict['details']}
  Resolution: {conflict['resolution'] or 'PENDING'}
"""

        validation = report["merged_results"].get("validation_issues", [])
        if validation:
            formatted += f"\n{'=' * 70}\n❌ VALIDATION ISSUES\n{'=' * 70}\n"
            for issue in validation:
                formatted += f"  • {issue}\n"

        return formatted

    def execute(self, action: Dict[str, str]) -> str:
        """Execute merging action"""
        act = action.get("action")

        if act == "collect_results":
            agent = action.get("agent")
            results = action.get("results", {})
            self.collect_agent_results(agent, results)
            return f"Collected results from {agent}"

        elif act == "resolve_conflict":
            conflict_type = action.get("conflict_type")
            agent1 = action.get("agent1", "Unknown")
            agent2 = action.get("agent2", "Unknown")
            details = action.get("details", "")
            resolution = action.get("resolution")

            self.resolve_conflicts(conflict_type, agent1, agent2, details)

            if resolution:
                for conflict in self.conflicts:
                    if conflict["conflict_type"] == conflict_type:
                        conflict["resolution"] = resolution
                        conflict["resolved_by"] = "MergingAgent"
                        conflict["resolved_at"] = datetime.now().isoformat()

                return f"Resolved conflict: {conflict_type}"

            return f"Logged conflict: {conflict_type}"

        elif act == "merge_results":
            self.merge_results()
            return "Merged all agent results"

        elif act == "generate_final_report":
            report = self.generate_final_report()
            return f"Generated final report ({len(report)} chars)"

        return "Unknown action"
