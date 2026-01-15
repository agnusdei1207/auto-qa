"""
Report Agent - Test Report Generation
"""
import json
import logging
from .base_agent import BaseAgent
from libs.database.src import repository as db


logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):
    """Generates final test reports"""
    
    def get_system_prompt(self) -> str:
        return """You are Report Agent for web automation testing.

Your role is to generate comprehensive test reports.

OUTPUT FORMAT:
{
  "summary": "Test execution summary",
  "total_tests": 10,
  "passed": 8,
  "failed": 2,
  "details": [
    {
      "test_case": "Test name",
      "status": "PASS|FAIL",
      "duration": "2.5s",
      "notes": "Additional notes"
    }
  ]
}"""
    
    def get_description(self) -> str:
        return "Report Agent - Generates test reports"
    
    def execute(self, action: Dict[str, str]) -> str:
        """Generate and save report"""
        try:
            session_id = self.session_id
            
            test_cases = db.get_test_cases_by_session(session_id)
            
            passed = sum(1 for tc in test_cases if tc.get("status") == "COMPLETED")
            failed = sum(1 for tc in test_cases if tc.get("status") == "FAILED")
            total = len(test_cases)
            
            report = {
                "session_id": session_id,
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
                "test_cases": test_cases
            }
            
            logger.info(f"📊 Report: {passed}/{total} passed ({(passed/total*100):.1f}%)" if total > 0 else "No test cases")
            
            return json.dumps(report, indent=2, default=str)
        
        except Exception as e:
            logger.error(f"Report agent error: {e}")
            return f"Error: {str(e)}"
