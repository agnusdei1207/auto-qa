"""
Git Automation - Auto commit and push after QA tests

Handles automatic git operations:
- Commit test results
- Create meaningful commit messages
- Push to remote repository
- Handle merge conflicts gracefully
"""
import subprocess
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


logger = logging.getLogger(__name__)


class GitManager:
    """Manages git operations for auto-commit/push"""

    def __init__(self, repo_path: str = ".", branch: str = "main"):
        self.repo_path = Path(repo_path).resolve()
        self.branch = branch

    def _run_git_command(self, *args, capture_output: bool = True) -> tuple[bool, str, str]:
        """Run git command and return (success, stdout, stderr)"""
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=False
            )
            success = result.returncode == 0
            return success, result.stdout or "", result.stderr or ""
        except Exception as e:
            logger.error(f"Git command error: {e}")
            return False, "", str(e)

    def is_git_repo(self) -> bool:
        """Check if directory is a git repository"""
        success, _, _ = self._run_git_command("rev-parse", "--git-dir")
        return success

    def get_current_branch(self) -> Optional[str]:
        """Get current branch name"""
        success, stdout, _ = self._run_git_command("rev-parse", "--abbrev-ref", "HEAD")
        if success:
            return stdout.strip()
        return None

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        success, stdout, _ = self._run_git_command("status", "--porcelain")
        if success:
            return len(stdout.strip()) > 0
        return False

    def add_files(self, file_patterns: list[str]) -> bool:
        """Add files to staging area"""
        success, _, stderr = self._run_git_command("add", *file_patterns)
        if not success:
            logger.error(f"Failed to add files: {stderr}")
            return False
        return True

    def commit_test_results(
        self,
        session_id: str,
        test_url: str,
        test_status: str,
        summary: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Commit test results with meaningful message"""

        if not self.has_uncommitted_changes():
            logger.info("No changes to commit")
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_emoji = "✅" if test_status == "COMPLETED" else "❌" if test_status == "FAILED" else "⏹️"

        # Build commit message
        commit_msg = f"""{status_emoji} QA Test Results - {timestamp}

Session ID: {session_id}
URL: {test_url}
Status: {test_status}
"""

        if summary:
            commit_msg += f"\nSummary:\n"
            for key, value in summary.items():
                commit_msg += f"  {key}: {value}\n"

        success, _, stderr = self._run_git_command("commit", "-m", commit_msg)
        if not success:
            logger.error(f"Failed to commit: {stderr}")
            return False

        logger.info(f"Committed test results for session {session_id}")
        return True

    def push_to_remote(self, remote: str = "origin", force: bool = False) -> bool:
        """Push changes to remote repository"""
        args = ["push"]
        if force:
            args.append("--force-with-lease")
        args.extend([remote, self.branch])

        success, _, stderr = self._run_git_command(*args)
        if not success:
            logger.error(f"Failed to push: {stderr}")
            return False

        logger.info(f"Pushed to {remote}/{self.branch}")
        return True

    def auto_commit_and_push(
        self,
        session_id: str,
        test_url: str,
        test_status: str,
        summary: Optional[Dict[str, Any]] = None,
        file_patterns: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Auto commit and push test results"""

        result = {
            "session_id": session_id,
            "success": False,
            "committed": False,
            "pushed": False,
            "error": None
        }

        try:
            # Check if git repo
            if not self.is_git_repo():
                result["error"] = "Not a git repository"
                return result

            # Add files (default to all changes)
            if file_patterns is None:
                file_patterns = ["."]
            if not self.add_files(file_patterns):
                result["error"] = "Failed to add files"
                return result

            # Commit
            if not self.commit_test_results(session_id, test_url, test_status, summary):
                result["error"] = "Failed to commit"
                return result

            result["committed"] = True

            # Push
            if not self.push_to_remote():
                result["error"] = "Failed to push"
                return result

            result["pushed"] = True
            result["success"] = True

        except Exception as e:
            logger.error(f"Auto commit/push error: {e}")
            result["error"] = str(e)

        return result

    def create_branch(self, branch_name: str) -> bool:
        """Create and checkout new branch"""
        success, _, stderr = self._run_git_command("checkout", "-b", branch_name)
        if not success:
            logger.error(f"Failed to create branch: {stderr}")
            return False
        self.branch = branch_name
        return True

    def get_remote_url(self) -> Optional[str]:
        """Get remote repository URL"""
        success, stdout, _ = self._run_git_command("remote", "get-url", "origin")
        if success:
            return stdout.strip()
        return None

    def get_last_commit(self) -> Optional[Dict[str, str]]:
        """Get last commit information"""
        success, stdout, _ = self._run_git_command(
            "log", "-1", "--pretty=format:%H|%an|%ad|%s", "--date=short"
        )
        if success:
            parts = stdout.split("|")
            if len(parts) >= 4:
                return {
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3]
                }
        return None
