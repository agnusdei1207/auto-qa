"""
Error Logger - Categorized Error Tracking

Logs, categorizes, and tracks all errors with detailed information.
Persists errors to files for safety.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error categories for classification"""
    NAVIGATION = "navigation"
    ELEMENT_NOT_FOUND = "element_not_found"
    TIMEOUT = "timeout"
    NETWORK = "network"
    FORM_VALIDATION = "form_validation"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    LOGIC = "logic"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorLogger:
    """Logs and categorizes errors with detailed tracking"""

    def __init__(self, session_id: str, log_dir: str = "/tmp/error_logs"):
        self.session_id = session_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.error_log_file = self.log_dir / f"{session_id}_errors.json"
        self.summary_file = self.log_dir / f"{session_id}_error_summary.json"

    def log_error(
        self,
        error: Exception,
        agent: str,
        action: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        step_number: Optional[int] = None,
        test_case_id: Optional[str] = None
    ):
        """Log a detailed error with categorization"""
        error_entry = {
            "error_id": self._generate_error_id(),
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "agent": agent,
            "action": action,
            "category": category.value,
            "severity": severity.value,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": self._format_traceback(error),
            "step_number": step_number,
            "test_case_id": test_case_id,
            "context": context or {},
            "resolved": False,
            "resolution_attempts": []
        }

        self._append_to_log(error_entry)
        self._update_summary(error_entry)

        logger.error(
            f"[{category.value.upper()}] {agent} - {action}: {error}"
        )

    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

    def _format_traceback(self, error: Exception) -> str:
        """Format error traceback"""
        import traceback
        return "".join(traceback.format_exception(type(error), error, error.__traceback__))

    def _append_to_log(self, error_entry: Dict[str, Any]):
        """Append error to log file"""
        errors = []
        if self.error_log_file.exists():
            with open(self.error_log_file, 'r') as f:
                errors = json.load(f)

        errors.append(error_entry)

        with open(self.error_log_file, 'w') as f:
            json.dump(errors, f, indent=2, default=str)

    def _update_summary(self, error_entry: Dict[str, Any]):
        """Update error summary statistics"""
        summary = {
            "session_id": self.session_id,
            "total_errors": 0,
            "by_category": {},
            "by_severity": {},
            "by_agent": {},
            "resolved": 0,
            "unresolved": 0,
            "last_updated": datetime.now().isoformat()
        }

        if self.summary_file.exists():
            with open(self.summary_file, 'r') as f:
                summary = json.load(f)

        summary["total_errors"] += 1

        category = error_entry["category"]
        severity = error_entry["severity"]
        agent = error_entry["agent"]

        summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        summary["by_agent"][agent] = summary["by_agent"].get(agent, 0) + 1

        summary["unresolved"] += 1

        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

    def mark_resolved(self, error_id: str, resolution: str):
        """Mark an error as resolved"""
        if not self.error_log_file.exists():
            return

        with open(self.error_log_file, 'r') as f:
            errors = json.load(f)

        for error in errors:
            if error["error_id"] == error_id:
                error["resolved"] = True
                error["resolution"] = resolution
                error["resolved_at"] = datetime.now().isoformat()
                error["resolution_attempts"].append({
                    "timestamp": datetime.now().isoformat(),
                    "resolution": resolution
                })

        with open(self.error_log_file, 'w') as f:
            json.dump(errors, f, indent=2, default=str)

        self._update_summary_resolution(error_id, True)

    def add_resolution_attempt(self, error_id: str, attempt: str):
        """Log a resolution attempt for an error"""
        if not self.error_log_file.exists():
            return

        with open(self.error_log_file, 'r') as f:
            errors = json.load(f)

        for error in errors:
            if error["error_id"] == error_id:
                error["resolution_attempts"].append({
                    "timestamp": datetime.now().isoformat(),
                    "attempt": attempt,
                    "success": False
                })

        with open(self.error_log_file, 'w') as f:
            json.dump(errors, f, indent=2, default=str)

    def _update_summary_resolution(self, error_id: str, resolved: bool):
        """Update summary when error is resolved"""
        if not self.summary_file.exists():
            return

        with open(self.summary_file, 'r') as f:
            summary = json.load(f)

        if resolved:
            summary["resolved"] += 1
        summary["unresolved"] = max(0, summary["unresolved"] - 1)

        summary["last_updated"] = datetime.now().isoformat()

        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

    def get_errors(self, category: Optional[ErrorCategory] = None) -> List[Dict[str, Any]]:
        """Get errors, optionally filtered by category"""
        if not self.error_log_file.exists():
            return []

        with open(self.error_log_file, 'r') as f:
            errors = json.load(f)

        if category:
            return [e for e in errors if e["category"] == category.value]

        return errors

    def get_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        if not self.summary_file.exists():
            return {
                "session_id": self.session_id,
                "total_errors": 0,
                "message": "No errors logged yet"
            }

        with open(self.summary_file, 'r') as f:
            return json.load(f)

    def get_critical_errors(self) -> List[Dict[str, Any]]:
        """Get all critical and high severity errors"""
        errors = self.get_errors()
        return [
            e for e in errors
            if e["severity"] in [ErrorSeverity.CRITICAL.value, ErrorSeverity.HIGH.value]
        ]

    def get_errors_by_agent(self, agent: str) -> List[Dict[str, Any]]:
        """Get errors for a specific agent"""
        errors = self.get_errors()
        return [e for e in errors if e["agent"] == agent]

    def get_unresolved_errors(self) -> List[Dict[str, Any]]:
        """Get all unresolved errors"""
        errors = self.get_errors()
        return [e for e in errors if not e["resolved"]]

    def generate_error_report(self) -> str:
        """Generate comprehensive error report"""
        summary = self.get_summary()
        errors = self.get_errors()

        report = f"""
{'=' * 60}
ERROR REPORT - Session {self.session_id}
{'=' * 60}

📊 Summary
{'=' * 60}
Total Errors: {summary['total_errors']}
Resolved: {summary.get('resolved', 0)}
Unresolved: {summary.get('unresolved', 0)}

By Category:
"""
        for category, count in summary.get('by_category', {}).items():
            report += f"  • {category.replace('_', ' ').title()}: {count}\n"

        report += "\nBy Severity:\n"
        for severity, count in summary.get('by_severity', {}).items():
            report += f"  • {severity.upper()}: {count}\n"

        report += "\nBy Agent:\n"
        for agent, count in summary.get('by_agent', {}).items():
            report += f"  • {agent}: {count}\n"

        critical_errors = self.get_critical_errors()
        if critical_errors:
            report += f"\n{'=' * 60}\n🚨 CRITICAL ERRORS ({len(critical_errors)})\n{'=' * 60}\n"
            for error in critical_errors[:5]:
                report += f"""
[ERROR ID: {error['error_id']}]
Agent: {error['agent']}
Action: {error['action']}
Severity: {error['severity'].upper()}
Message: {error['error_message']}
Resolved: {'Yes' if error['resolved'] else 'No'}
Timestamp: {error['timestamp'][:19]}
"""

        return report

    def export_errors_to_csv(self, output_path: str):
        """Export errors to CSV file"""
        import csv

        errors = self.get_errors()

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)

            writer.writerow([
                'Error ID', 'Timestamp', 'Agent', 'Action',
                'Category', 'Severity', 'Error Type',
                'Error Message', 'Test Case ID', 'Step Number',
                'Resolved', 'Resolution'
            ])

            for error in errors:
                writer.writerow([
                    error['error_id'],
                    error['timestamp'],
                    error['agent'],
                    error['action'],
                    error['category'],
                    error['severity'],
                    error['error_type'],
                    error['error_message'],
                    error.get('test_case_id', ''),
                    error.get('step_number', ''),
                    'Yes' if error['resolved'] else 'No',
                    error.get('resolution', '')
                ])

        logger.info(f"Exported {len(errors)} errors to {output_path}")
