"""
HTML Analyzer Agent - HTML-based Testing (Refactored)

Analyzes page HTML structure instead of visual testing.
Validates accessibility, semantics, and structure.

Refactored to use separate HTMLChecks class for validation logic.
"""
import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from apps.brain.src.config import EXECUTOR_API_URL
import requests
from .html_checks import HTMLChecks

logger = logging.getLogger(__name__)


class HTMLAnalyzerAgent(BaseAgent):
    """Analyzes HTML structure, accessibility, and semantics"""

    def __init__(self, session_id: str, llm):
        super().__init__(session_id, llm)
        self.checks = HTMLChecks()

    def get_system_prompt(self) -> str:
        return """You are HTML Analyzer Agent for web automation testing.

Your role is to analyze HTML structure instead of visual testing.

ANALYSIS AREAS:
- Semantic HTML (proper use of tags)
- Accessibility (alt tags, ARIA labels, form labels)
- Structure (proper nesting, valid HTML)
- Performance (inline scripts, large DOM)
- SEO (meta tags, headings hierarchy)
- Forms (validation, labels, error messages)

OUTPUT FORMAT:
{
  "action": "analyze_html|check_accessibility|validate_structure",
  "check_type": "type of check",
  "selector": "CSS selector (if applicable)",
  "expected": "expected result",
  "severity": "critical|warning|info"
}"""

    def get_description(self) -> str:
        return "HTML Analyzer - HTML structure and accessibility analysis"

    def execute(self, action: Dict[str, str]) -> str:
        """Execute HTML analysis action"""
        try:
            act = action.get("action")

            if act == "analyze_html":
                return self._analyze_full_html()

            elif act == "check_accessibility":
                return self._check_accessibility()

            elif act == "validate_structure":
                return self._validate_structure()

            elif act == "check_forms":
                return self._check_forms()

            elif act == "check_semantics":
                return self._check_semantics()

            return "Unknown action"

        except Exception as e:
            logger.error(f"HTML analyzer error: {e}")
            return f"Error: {str(e)}"

    def _get_html(self) -> tuple[str, str]:
        """Fetch HTML from executor API"""
        try:
            payload = {"session_id": self.session_id}
            res = requests.post(
                f"{EXECUTOR_API_URL}/get_html",
                json=payload,
                timeout=30
            )
            data = res.json()

            if not data.get("success"):
                raise Exception("Failed to get HTML")

            html = data.get("html", "")
            url = data.get("url", "unknown")

            return html, url

        except Exception as e:
            logger.error(f"Failed to fetch HTML: {e}")
            raise

    def _analyze_full_html(self) -> str:
        """Perform comprehensive HTML analysis"""
        try:
            html, url = self._get_html()

            analysis = {
                "url": url,
                "html_length": len(html),
                "issues": [],
                "warnings": [],
                "info": []
            }

            analysis["issues"].extend(self.checks.check_critical_issues(html))
            analysis["warnings"].extend(self.checks.check_warnings(html))
            analysis["info"].extend(self.checks.check_info(html))

            return self._format_analysis(analysis)

        except Exception as e:
            return f"HTML analysis failed: {str(e)}"

    def _check_accessibility(self) -> str:
        """Check accessibility issues"""
        try:
            html, _ = self._get_html()
            issues = []

            issues.append(self.checks.check_images_have_alt(html))
            issues.append(self.checks.check_forms_have_labels(html))
            issues.append(self.checks.check_heading_hierarchy(html))
            issues.append(self.checks.check_aria_labels(html))

            results = [i for i in issues if i]

            if results:
                return f"Found {len(results)} accessibility issues:\n" + "\n".join(results)
            else:
                return "✅ No accessibility issues found"

        except Exception as e:
            return f"Accessibility check failed: {str(e)}"

    def _validate_structure(self) -> str:
        """Validate HTML structure"""
        try:
            html, _ = self._get_html()
            issues = []

            if html.count("<body>") > 1:
                issues.append("Multiple <body> tags found")

            if html.count("<html>") > 1:
                issues.append("Multiple <html> tags found")

            unclosed_tags = self.checks.find_unclosed_tags(html)
            if unclosed_tags:
                issues.append(f"Unclosed tags: {', '.join(unclosed_tags)}")

            if issues:
                return f"Structure issues:\n" + "\n".join(issues)
            else:
                return "✅ HTML structure is valid"

        except Exception as e:
            return f"Structure validation failed: {str(e)}"

    def _check_forms(self) -> str:
        """Check form validation and accessibility"""
        try:
            html, _ = self._get_html()
            issues = []

            issues.append(self.checks.check_form_required_attributes(html))
            issues.append(self.checks.check_form_input_types(html))
            issues.append(self.checks.check_form_error_handling(html))

            results = [i for i in issues if i]

            if results:
                return f"Form issues:\n" + "\n".join(results)
            else:
                return "✅ Forms are properly configured"

        except Exception as e:
            return f"Form check failed: {str(e)}"

    def _check_semantics(self) -> str:
        """Check semantic HTML usage"""
        try:
            html, _ = self._get_html()
            issues = []

            issues.extend(self.checks.check_semantic_tags(html))
            issues.extend(self.checks.check_div_usage(html))
            issues.extend(self.checks.check_heading_structure(html))

            if issues:
                return f"Semantic issues:\n" + "\n".join(issues)
            else:
                return "✅ Semantic HTML is properly used"

        except Exception as e:
            return f"Semantic check failed: {str(e)}"

    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format HTML analysis results"""
        result = f"""
 📊 HTML Analysis Report
 {'=' * 50}

 🌐 URL: {analysis['url']}
 📏 HTML Length: {analysis['html_length']:,} characters

 {'=' * 50}

 ❌ Critical Issues ({len(analysis['issues'])})
"""
        if analysis['issues']:
            for issue in analysis['issues']:
                result += f"  • {issue}\n"
        else:
            result += "  None\n"

        result += f"\n⚠️  Warnings ({len(analysis['warnings'])})\n"
        if analysis['warnings']:
            for warning in analysis['warnings']:
                result += f"  • {warning}\n"
        else:
            result += "  None\n"

        result += f"\nℹ️  Information ({len(analysis['info'])})\n"
        if analysis['info']:
            for info in analysis['info']:
                result += f"  • {info}\n"
        else:
            result += "  None\n"

        return result
