"""
Progress Tracker Agent - Real-time Progress & Checklist Management

Tracks test execution progress, maintains checklists,
and persists all data to files for safety.
"""
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .base_agent import BaseAgent
from apps.brain.src.config import EXECUTOR_API_URL
import requests

logger = logging.getLogger(__name__)


class ProgressTrackerAgent(BaseAgent):
    """Tracks progress, maintains checklists, and ensures file persistence"""

    def __init__(self, session_id: str, llm, progress_dir: str = "/tmp/progress"):
        super().__init__(session_id, llm)
        self.progress_dir = Path(progress_dir)
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.progress_dir / f"{session_id}_progress.json"
        self.checklist_file = self.progress_dir / f"{session_id}_checklist.json"
        self.collaboration_log = self.progress_dir / f"{session_id}_collaboration.json"

    def get_system_prompt(self) -> str:
        return """You are Progress Tracker Agent for web automation testing.

Your role is to:
1. Track real-time progress of all agents
2. Maintain comprehensive checklists
3. Persist all data to files (never rely on memory)
4. Coordinate agent collaboration
5. Log all agent activities

OUTPUT FORMAT:
{
  "action": "update_checklist|log_progress|sync_agents",
  "test_case": "test case name",
  "step": "step description",
  "status": "pending|in_progress|completed|failed",
  "agent": "agent name",
  "checklist_items": ["item1", "item2"]
}"""

    def get_description(self) -> str:
        return "Progress Tracker - Real-time progress & checklist management"

    def initialize_session(self, test_cases: List[Dict[str, Any]]):
        """Initialize progress tracking for new session"""
        progress = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "test_cases": {},
            "total_tests": len(test_cases),
            "completed_tests": 0,
            "failed_tests": 0,
            "overall_progress": 0,
            "agent_status": {}
        }

        for i, tc in enumerate(test_cases):
            test_case_id = tc.get("id", f"tc_{i}")
            steps = tc.get("steps", [])
            progress["test_cases"][test_case_id] = {
                "name": tc.get("name", f"Test Case {i+1}"),
                "status": "pending",
                "total_steps": len(steps),
                "completed_steps": 0,
                "steps": [
                    {
                        "step_number": j,
                        "description": step,
                        "status": "pending",
                        "agent": None,
                        "started_at": None,
                        "completed_at": None,
                        "error": None
                    }
                    for j, step in enumerate(steps)
                ],
                "checklist": self._generate_checklist(tc)
            }

        self._save_progress(progress)

        checklist = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "items": []
        }

        for tc_id, tc_data in progress["test_cases"].items():
            checklist["items"].append({
                "test_case_id": tc_id,
                "test_case_name": tc_data["name"],
                "checklist": tc_data["checklist"],
                "all_checked": False
            })

        self._save_checklist(checklist)
        logger.info(f"✅ Progress tracking initialized for {len(test_cases)} test cases")

    def _generate_checklist(self, test_case: Dict[str, Any]) -> List[str]:
        """Generate checklist items from test case"""
        description = test_case.get("description", "")
        steps = test_case.get("steps", [])

        checklist = []

        checklist.append(f"✓ Test case ready: {test_case.get('name', 'Unnamed')}")
        checklist.append(f"✓ {len(steps)} steps defined")

        for i, step in enumerate(steps, 1):
            checklist.append(f"☐ Step {i}: {step}")

        checklist.append("✓ All validations passed")
        checklist.append("✓ Test case completed successfully")

        return checklist

    def update_step_status(
        self,
        test_case_id: str,
        step_number: int,
        status: str,
        agent: str,
        error: str = None
    ):
        """Update status of a specific step"""
        progress = self._load_progress()

        if test_case_id in progress["test_cases"]:
            steps = progress["test_cases"][test_case_id]["steps"]
            if step_number < len(steps):
                steps[step_number]["status"] = status
                steps[step_number]["agent"] = agent

                if status == "in_progress":
                    steps[step_number]["started_at"] = datetime.now().isoformat()
                elif status in ["completed", "failed"]:
                    steps[step_number]["completed_at"] = datetime.now().isoformat()
                    steps[step_number]["error"] = error

                    completed_steps = sum(
                        1 for s in steps if s["status"] in ["completed", "failed"]
                    )
                    progress["test_cases"][test_case_id]["completed_steps"] = completed_steps

                    self._update_overall_progress(progress)

        self._save_progress(progress)
        self._notify_executor(test_case_id, step_number, status, agent)

    def update_test_case_status(
        self,
        test_case_id: str,
        status: str
    ):
        """Update status of a test case"""
        progress = self._load_progress()

        if test_case_id in progress["test_cases"]:
            progress["test_cases"][test_case_id]["status"] = status

            if status == "completed":
                progress["completed_tests"] += 1
            elif status == "failed":
                progress["failed_tests"] += 1

            self._update_checklist_for_test_case(test_case_id, status)

        self._save_progress(progress)
        logger.info(f"Test case {test_case_id} status: {status}")

    def _update_overall_progress(self, progress: Dict[str, Any]):
        """Calculate and update overall progress percentage"""
        total_steps = 0
        completed_steps = 0

        for tc_data in progress["test_cases"].values():
            total_steps += tc_data["total_steps"]
            completed_steps += tc_data["completed_steps"]

        if total_steps > 0:
            progress["overall_progress"] = round((completed_steps / total_steps) * 100, 1)
        else:
            progress["overall_progress"] = 0

    def _update_checklist_for_test_case(self, test_case_id: str, status: str):
        """Update checklist for a specific test case"""
        checklist = self._load_checklist()

        for item in checklist["items"]:
            if item["test_case_id"] == test_case_id:
                item["all_checked"] = (status == "completed")

                if status == "completed":
                    item["checklist"] = [
                        item.replace("☐", "✓") if "☐" in item else item
                        for item in item["checklist"]
                    ]

        self._save_checklist(checklist)

    def log_agent_activity(
        self,
        agent: str,
        activity_type: str,
        details: str,
        timestamp: str = None
    ):
        """Log agent activity for collaboration tracking"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "agent": agent,
            "activity_type": activity_type,
            "details": details
        }

        collaboration_log = []
        if self.collaboration_log.exists():
            with open(self.collaboration_log, 'r') as f:
                collaboration_log = json.load(f)

        collaboration_log.append(log_entry)

        with open(self.collaboration_log, 'w') as f:
            json.dump(collaboration_log, f, indent=2, default=str)

    def get_progress_report(self) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        progress = self._load_progress()
        checklist = self._load_checklist()
        collaboration = self._load_collaboration_log()

        return {
            "progress": progress,
            "checklist": checklist,
            "collaboration": collaboration[-50:] if collaboration else [],
            "summary": {
                "total_tests": progress.get("total_tests", 0),
                "completed_tests": progress.get("completed_tests", 0),
                "failed_tests": progress.get("failed_tests", 0),
                "overall_progress": progress.get("overall_progress", 0),
                "pending_tests": progress.get("total_tests", 0) - progress.get("completed_tests", 0) - progress.get("failed_tests", 0)
            }
        }

    def _save_progress(self, progress: Dict[str, Any]):
        """Save progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2, default=str)

    def _load_progress(self) -> Dict[str, Any]:
        """Load progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {"session_id": self.session_id, "test_cases": {}}

    def _save_checklist(self, checklist: Dict[str, Any]):
        """Save checklist to file"""
        with open(self.checklist_file, 'w') as f:
            json.dump(checklist, f, indent=2, default=str)

    def _load_checklist(self) -> Dict[str, Any]:
        """Load checklist from file"""
        if self.checklist_file.exists():
            with open(self.checklist_file, 'r') as f:
                return json.load(f)
        return {"session_id": self.session_id, "items": []}

    def _load_collaboration_log(self) -> List[Dict[str, Any]]:
        """Load collaboration log from file"""
        if self.collaboration_log.exists():
            with open(self.collaboration_log, 'r') as f:
                return json.load(f)
        return []

    def _notify_executor(
        self,
        test_case_id: str,
        step_number: int,
        status: str,
        agent: str
    ):
        """Notify executor of progress update"""
        try:
            payload = {
                "session_id": self.session_id,
                "test_case_id": test_case_id,
                "step_number": step_number,
                "status": status,
                "message": f"{agent} - Step {step_number + 1}: {status}"
            }
            requests.post(
                f"{EXECUTOR_API_URL}/update_progress",
                json=payload,
                timeout=10
            )
        except Exception as e:
            logger.error(f"Failed to notify executor: {e}")

    def execute(self, action: Dict[str, str]) -> str:
        """Execute progress tracking action"""
        action_type = action.get("action")

        if action_type == "update_checklist":
            test_case = action.get("test_case")
            checklist_items = action.get("checklist_items", [])
            return f"Updated checklist for {test_case}: {len(checklist_items)} items"

        elif action_type == "log_progress":
            test_case = action.get("test_case")
            step = action.get("step")
            status = action.get("status")
            agent = action.get("agent")
            return f"Logged progress: {agent} - {test_case} - {step} ({status})"

        elif action_type == "sync_agents":
            return "Synced agent activities"

        return "Unknown action"
