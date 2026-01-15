"""
QA Brain Loop - Main orchestration loop with async parallel execution
"""
import asyncio
import logging
import os
from typing import Optional

from apps.brain.src.agents.navigation_agent import NavigationAgent
from apps.brain.src.agents.form_agent import FormAgent
from apps.brain.src.agents.interaction_agent import InteractionAgent
from apps.brain.src.agents.verification_agent import VerificationAgent
from apps.brain.src.agents.report_agent import ReportAgent
from apps.brain.src.agents.merging_agent import MergingAgent
from apps.brain.src.agents.enhanced_orchestrator import EnhancedOrchestrator
from apps.brain.src.core.llm_client import LLMClient
from apps.brain.src.core.prompts import PromptBuilder
from libs.database.src import repository as db
from libs.database.src.error_logger import ErrorLogger
from libs.git_automation.src.git_manager import GitManager


logger = logging.getLogger(__name__)


async def run_brain_loop_async(session_id: str, url: str, domain_info: str, check_running):
    """Main QA testing loop with async support"""

    logger.info(f"🧠 Starting Enhanced QA Brain for session {session_id}")

    llm = LLMClient(session_id)
    error_logger = ErrorLogger(session_id)
    git_manager = None

    # Initialize Git manager if git repo
    git_enabled = os.getenv("ENABLE_GIT_AUTO_COMMIT", "false").lower() == "true"
    if git_enabled:
        git_manager = GitManager(repo_path=os.getenv("GIT_REPO_PATH", "."))

    db.update_session_status(session_id, "RUNNING", "EnhancedOrchestrator")

    try:
        # Generate initial test cases from domain info
        prompt = PromptBuilder.build_qa_prompt(url, domain_info)
        test_case_response = await asyncio.to_thread(llm.generate, prompt, "Planning")

        from apps.brain.src.core.parser import parse_test_cases
        test_cases = parse_test_cases(test_case_response)

        logger.info(f"📋 Generated {len(test_cases)} test cases")

        # Create test cases in database
        for tc in test_cases:
            test_case_id = await asyncio.to_thread(
                db.create_test_case,
                session_id=session_id,
                name=tc.get("name", "Unnamed Test"),
                description=tc.get("description", "")
            )
            logger.info(f"✓ Created test case: {tc.get('name')}")

        # Initialize agents
        max_parallel = int(os.getenv("MAX_PARALLEL_AGENTS", "4"))
        agents = [
            NavigationAgent(session_id, llm),
            FormAgent(session_id, llm),
            InteractionAgent(session_id, llm),
            VerificationAgent(session_id, llm),
            ReportAgent(session_id, llm),
            MergingAgent(session_id, llm, error_logger)
        ]

        orchestrator = EnhancedOrchestrator(session_id, llm, agents, max_parallel)

        # Run async orchestration
        success = await orchestrator.orchestrate(url, domain_info, check_running)

        # Auto-commit git if enabled
        if success and git_manager:
            logger.info("📝 Auto-committing test results to git...")
            git_result = await asyncio.to_thread(
                git_manager.auto_commit_and_push,
                session_id=session_id,
                test_url=url,
                test_status="COMPLETED",
                summary={
                    "test_cases": len(test_cases),
                    "domain": domain_info[:100]
                }
            )
            if git_result["success"]:
                logger.info(f"✅ Git auto-commit successful: pushed to {git_manager.get_current_branch()}")
            else:
                logger.warning(f"⚠️  Git auto-commit failed: {git_result.get('error')}")

        if success:
            await asyncio.to_thread(db.update_session_status, session_id, "COMPLETED")
            logger.info("✅ QA Brain completed successfully")
        else:
            await asyncio.to_thread(db.update_session_status, session_id, "STOPPED")
            logger.info("⏹️  QA Brain stopped")

    except Exception as e:
        logger.error(f"QA Brain error: {e}")
        import traceback
        traceback.print_exc()
        await asyncio.to_thread(db.update_session_status, session_id, "ERROR", notes=str(e))


def run_brain_loop(session_id: str, url: str, domain_info: str, check_running):
    """Main QA testing loop (sync wrapper for async)"""
    # Run async event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            run_brain_loop_async(session_id, url, domain_info, check_running)
        )
    finally:
        loop.close()
