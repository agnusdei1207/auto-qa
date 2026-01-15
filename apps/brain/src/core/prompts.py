"""
Prompt Builder Module
"""
import json
from typing import Dict, List


class PromptBuilder:
    """Builder for LLM prompts."""

    @staticmethod
    def build_qa_prompt(url: str, domain_info: str, context: str = "") -> str:
        """Constructs main QA prompt."""
        return """You are an expert QA tester specializing in web automation.

🌐 Target URL: """ + url + """

📋 Domain Information:
""" + domain_info + """
""" + context + """

🎯 Your Mission:
Analyze the domain information and create comprehensive test cases for this website.

💡 Consider:
- User flows (registration, login, checkout, etc.)
- Form validation (required fields, data formats)
- Navigation (links, buttons, menus)
- Interactive elements (drag and drop, modals, tabs)
- Responsive design (mobile, desktop)
- Accessibility (alt tags, ARIA labels)

OUTPUT FORMAT:
""" + json.dumps({
    "thinking": "Analysis of the domain",
    "test_cases": [
        {
            "name": "Test case name",
            "description": "Detailed description",
            "steps": ["Step 1", "Step 2"]
        }
    ]
}, indent=4) + """

    @staticmethod
    def build_micro_test_prompt(url: str, domain_info: str) -> str:
        """Constructs micro-test generation prompt for granular steps."""
        return """You are an expert QA tester specializing in granular micro-testing.

🌐 Target URL: """ + url + """

📋 Domain Information:
""" + domain_info + """

🎯 Your Mission:
Break down test scenarios into MICRO-LEVEL granular steps.
Each step should be atomic and executable independently.

MICRO-TEST PRINCIPLES:
- Each step must be a single, verifiable action
- Steps must be atomic (no compound actions)
- Each step should be testable independently
- Include specific selectors where possible
- Account for success/failure at each step

BREAKDOWN LEVELS:
1. Macro Test: "Login to account"
   → Micro Steps:
     1. Navigate to login page
     2. Enter username in username field
     3. Enter password in password field
     4. Click login button
     5. Verify redirect to dashboard
     6. Verify user name displayed

2. Macro Test: "Add item to cart"
   → Micro Steps:
     1. Navigate to product page
     2. Verify product details visible
     3. Click add to cart button
     4. Verify cart badge count increased
     5. Click cart icon
     6. Verify product in cart

OUTPUT FORMAT:
""" + json.dumps({
    "thinking": "Analysis and breakdown strategy",
    "micro_test_cases": [
        {
            "macro_test": "High-level test name",
            "priority": "critical|high|medium|low",
            "micro_steps": [
                {
                    "step_number": 1,
                    "action": "navigate|click|fill|verify|wait",
                    "description": "Atomic action description",
                    "selector": "CSS selector (if applicable)",
                    "value": "value to input (if applicable)",
                    "expected": "Expected result",
                    "verification": "How to verify success",
                    "estimated_time": "seconds"
                }
            ]
        }
    ]
}, indent=4)

    @staticmethod
    def build_parallel_execution_prompt(test_cases: List[Dict], available_agents: List[str]) -> str:
        """Constructs parallel execution planning prompt."""
        return """You are a task distribution specialist for parallel agent execution.

📋 Available Test Cases: """ + str(len(test_cases)) + """
🤖 Available Agents: """ + ', '.join(available_agents) + """

🎯 Your Mission:
Plan parallel execution of test cases across multiple agents.

PARALLEL EXECUTION PRINCIPLES:
- Identify independent test cases that can run in parallel
- Group dependent test cases that must run sequentially
- Balance workload across available agents
- Prioritize critical tests
- Minimize wait time between tasks

AGENT SPECIALIZATIONS:
- NavigationAgent: Page navigation, URL routing
- FormAgent: Form handling, validation, submission
- InteractionAgent: Clicks, hovers, drags, scrolls
- VerificationAgent: Text, element, URL, title verification
- HTMLAnalyzerAgent: HTML structure, accessibility analysis
- ProgressTrackerAgent: Progress tracking, checkpoint management
- MergingAgent: Result merging, conflict resolution

TASK DISTRIBUTION STRATEGY:
1. Group independent test cases
2. Assign to compatible agents
3. Create execution timeline
4. Identify merge points for parallel results

OUTPUT FORMAT:
""" + json.dumps({
    "thinking": "Execution strategy and reasoning",
    "execution_plan": {
        "parallel_groups": [
            {
                "group_id": 1,
                "test_cases": ["test_case_id_1", "test_case_id_2"],
                "agents": ["Agent1", "Agent2"],
                "can_run_parallel": True
            }
        ],
        "sequential_dependencies": [
            {
                "after_group": 1,
                "test_cases": ["test_case_id_3"],
                "agents": ["Agent3"],
                "reason": "Depends on group 1 results"
            }
        ],
        "merge_points": [
            {
                "after_groups": [1, 2],
                "action": "merge_results",
                "priority": 1
            }
        ],
        "estimated_duration": "minutes",
        "total_parallel_groups": 2
    }
}, indent=4)

    @staticmethod
    def build_action_prompt(page_context: str, test_step: str) -> str:
        """Constructs action generation prompt."""
        return """You are a web automation expert.

📄 Page Context:
""" + page_context + """

🎯 Test Step: """ + test_step + """

💡 Your Task:
Determine the specific action to execute (click, fill, drag, etc.).

OUTPUT FORMAT:
""" + json.dumps({
    "action_type": "click|fill|drag|hover|wait|navigate",
    "selector": "CSS selector",
    "value": "value to fill (if applicable)",
    "expected_result": "What should happen"
}, indent=4)

    @staticmethod
    def build_progress_prompt(
        current_status: str,
        completed_steps: int,
        total_steps: int
    ) -> str:
        """Constructs progress tracking prompt."""
        progress_pct = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        return """You are Progress Tracker Agent.

📊 Current Status: """ + current_status + """
✅ Completed: """ + str(completed_steps) + "/" + str(total_steps) + \
        " (" + str(round(progress_pct, 1)) + "%" if total_steps > 0 else "0%" + """

🎯 Your Mission:
Track and report progress accurately.

PROGRESS TRACKING TASKS:
- Update checklist status
- Log agent activities
- Identify bottlenecks
- Report completion percentage
- Estimate remaining time

OUTPUT FORMAT:
""" + json.dumps({
    "current_status": "running|paused|completed|error",
    "progress_percentage": round(progress_pct, 1),
    "completed_steps": completed_steps,
    "remaining_steps": total_steps - completed_steps if total_steps > 0 else 0,
    "estimated_completion": "ISO timestamp or time remaining",
    "checklist_updates": [
        {
            "test_case_id": "tc_id",
            "step_number": 1,
            "status": "completed|in_progress|pending",
            "agent": "agent_name"
        }
    ],
    "agent_status_report": {
        "NavigationAgent": "status",
        "FormAgent": "status",
        "InteractionAgent": "status",
        "VerificationAgent": "status",
        "HTMLAnalyzerAgent": "status"
    }
}, indent=4)
