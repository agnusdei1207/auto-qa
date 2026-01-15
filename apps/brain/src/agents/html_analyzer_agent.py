"""
HTML Analyzer Agent - HTML-based Testing

Analyzes page HTML structure instead of visual testing.
Validates accessibility, semantics, and structure.
"""
import re
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent
from apps.brain.src.config import EXECUTOR_API_URL
import requests

logger = logging.getLogger(__name__)


class HTMLAnalyzerAgent(BaseAgent):
    """Analyzes HTML structure, accessibility, and semantics"""

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
                return self._check_accessibility(action)

            elif act == "validate_structure":
                return self._validate_structure(action)

            elif act == "check_forms":
                return self._check_forms(action)

            elif act == "check_semantics":
                return self._check_semantics()

            return "Unknown action"

        except Exception as e:
            logger.error(f"HTML analyzer error: {e}")
            return f"Error: {str(e)}"

    def _analyze_full_html(self) -> str:
        """Perform comprehensive HTML analysis"""
        try:
            payload = {"session_id": self.session_id}
            res = requests.post(
                f"{EXECUTOR_API_URL}/get_html",
                json=payload,
                timeout=30
            )
            data = res.json()

            if not data.get("success"):
                return "Failed to get HTML"

            html = data.get("html", "")
            url = data.get("url", "unknown")

            analysis = {
                "url": url,
                "html_length": len(html),
                "issues": [],
                "warnings": [],
                "info": []
            }

            analysis["issues"].extend(self._check_critical_issues(html))
            analysis["warnings"].extend(self._check_warnings(html))
            analysis["info"].extend(self._check_info(html))

            return self._format_analysis(analysis)

        except Exception as e:
            return f"HTML analysis failed: {str(e)}"

    def _check_accessibility(self, action: Dict[str, str]) -> str:
        """Check accessibility issues"""
        try:
            payload = {"session_id": self.session_id}
            res = requests.post(
                f"{EXECUTOR_API_URL}/get_html",
                json=payload,
                timeout=30
            )
            data = res.json()

            if not data.get("success"):
                return "Failed to get HTML for accessibility check"

            html = data.get("html", "")
            issues = []

            issues.append(self._check_images_have_alt(html))
            issues.append(self._check_forms_have_labels(html))
            issues.append(self._check_heading_hierarchy(html))
            issues.append(self._check_aria_labels(html))

            results = [i for i in issues if i]

            if results:
                return f"Found {len(results)} accessibility issues:\n" + "\n".join(results)
            else:
                return "✅ No accessibility issues found"

        except Exception as e:
            return f"Accessibility check failed: {str(e)}"

    def _validate_structure(self, action: Dict[str, str]) -> str:
        """Validate HTML structure"""
        try:
            payload = {"session_id": self.session_id}
            res = requests.post(
                f"{EXECUTOR_API_URL}/get_html",
                json=payload,
                timeout=30
            )
            data = res.json()

            if not data.get("success"):
                return "Failed to get HTML for structure validation"

            html = data.get("html", "")
            issues = []

            if html.count("<body>") > 1:
                issues.append("Multiple <body> tags found")

            if html.count("<html>") > 1:
                issues.append("Multiple <html> tags found")

            unclosed_tags = self._find_unclosed_tags(html)
            if unclosed_tags:
                issues.append(f"Unclosed tags: {', '.join(unclosed_tags)}")

            if issues:
                return f"Structure issues:\n" + "\n".join(issues)
            else:
                return "✅ HTML structure is valid"

        except Exception as e:
            return f"Structure validation failed: {str(e)}"

    def _check_forms(self, action: Dict[str, str]) -> str:
        """Check form validation and accessibility"""
        try:
            payload = {"session_id": self.session_id}
            res = requests.post(
                f"{EXECUTOR_API_URL}/get_html",
                json=payload,
                timeout=30
            )
            data = res.json()

            if not data.get("success"):
                return "Failed to get HTML for form check"

            html = data.get("html", "")
            issues = []

            issues.append(self._check_form_required_attributes(html))
            issues.append(self._check_form_input_types(html))
            issues.append(self._check_form_error_handling(html))

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
            payload = {"session_id": self.session_id}
            res = requests.post(
                f"{EXECUTOR_API_URL}/get_html",
                json=payload,
                timeout=30
            )
            data = res.json()

            if not data.get("success"):
                return "Failed to get HTML for semantic check"

            html = data.get("html", "")
            issues = []

            semantic_tags = [
                "header", "nav", "main", "article", "section",
                "aside", "footer", "figure", "figcaption"
            ]

            if not any(tag in html for tag in semantic_tags):
                issues.append("No semantic HTML tags found")

            if "<div>" in html and "<span>" in html:
                div_count = html.count("<div>")
                issues.append(f"High <div> usage ({div_count} instances) - consider semantic tags")

            heading_structure = re.findall(r'<h([1-6])>', html)
            if heading_structure:
                if heading_structure[0] != '1':
                    issues.append(f"First heading is H{heading_structure[0]}, should be H1")

            if issues:
                return f"Semantic issues:\n" + "\n".join(issues)
            else:
                return "✅ Semantic HTML is properly used"

        except Exception as e:
            return f"Semantic check failed: {str(e)}"

    def _check_critical_issues(self, html: str) -> List[str]:
        """Check for critical HTML issues"""
        issues = []

        if not html.strip():
            issues.append("Empty HTML content")

        if "<script>" in html.lower() and "javascript:" in html.lower():
            issues.append("Inline JavaScript detected - potential security risk")

        return issues

    def _check_warnings(self, html: str) -> List[str]:
        """Check for HTML warnings"""
        warnings = []

        if html.count("<div>") > 50:
            warnings.append(f"High <div> count ({html.count('<div>')}) - may indicate layout complexity")

        if len(html) > 200000:
            warnings.append(f"Large HTML ({len(html)} chars) - consider optimization")

        return warnings

    def _check_info(self, html: str) -> List[str]:
        """Check for informational items"""
        info = []

        if "<meta " in html:
            meta_tags = re.findall(r'<meta[^>]+>', html)
            info.append(f"Found {len(meta_tags)} meta tags")

        viewport = re.search(r'<meta[^>]*viewport[^>]*>', html)
        if viewport:
            info.append("Viewport meta tag present")

        charset = re.search(r'<meta[^>]*charset[^>]*>', html)
        if charset:
            info.append("Charset meta tag present")

        return info

    def _check_images_have_alt(self, html: str) -> str:
        """Check if all images have alt attributes"""
        images = re.findall(r'<img[^>]+>', html, re.IGNORECASE)
        no_alt = [img for img in images if 'alt=' not in img.lower()]

        if no_alt:
            return f"⚠️  {len(no_alt)} images missing alt attribute"
        return None

    def _check_forms_have_labels(self, html: str) -> str:
        """Check if form inputs have labels"""
        inputs = re.findall(r'<input[^>]+>', html, re.IGNORECASE)
        unlabeled = [inp for inp in inputs if 'id=' in inp.lower()]

        if unlabeled:
            return f"⚠️  {len(unlabeled)} inputs may lack labels"
        return None

    def _check_heading_hierarchy(self, html: str) -> str:
        """Check heading hierarchy"""
        headings = re.findall(r'<h([1-6])', html, re.IGNORECASE)

        if not headings:
            return None

        if headings[0] != '1':
            return f"⚠️  First heading is H{headings[0]}, should be H1"

        return None

    def _check_aria_labels(self, html: str) -> str:
        """Check ARIA labels for interactive elements"""
        buttons = re.findall(r'<button[^>]*>(.*?)</button>', html, re.IGNORECASE)
        no_aria = [btn for btn in buttons if 'aria-label=' not in btn.lower() and not any(w in btn.lower() for w in ['>', 'icon', 'btn', '×'])]

        if no_aria:
            return f"⚠️  {len(no_aria)} buttons may need aria-label"
        return None

    def _find_unclosed_tags(self, html: str) -> List[str]:
        """Find potentially unclosed HTML tags"""
        common_tags = ['div', 'span', 'p', 'a', 'li']
        unclosed = []

        for tag in common_tags:
            opens = html.count(f'<{tag}')
            closes = html.count(f'</{tag}>')

            if opens > closes:
                unclosed.append(tag)

        return unclosed

    def _check_form_required_attributes(self, html: str) -> str:
        """Check if required form fields are marked"""
        required_fields = re.findall(r'<input[^>]*required[^>]*>', html, re.IGNORECASE)

        if not required_fields:
            return None

        return f"ℹ️  Found {len(required_fields)} required form fields"

    def _check_form_input_types(self, html: str) -> str:
        """Check form input types"""
        email_inputs = re.findall(r'<input[^>]*type=["\']?email["\']?[^>]*>', html, re.IGNORECASE)
        password_inputs = re.findall(r'<input[^>]*type=["\']?password["\']?[^>]*>', html, re.IGNORECASE)

        issues = []
        if email_inputs and 'type="email"' not in str(email_inputs):
            issues.append(f"Email field should use type=\"email\"")
        if password_inputs and 'type="password"' not in str(password_inputs):
            issues.append(f"Password field should use type=\"password\"")

        return "\n".join(issues) if issues else None

    def _check_form_error_handling(self, html: str) -> str:
        """Check for form error handling"""
        error_elements = re.findall(r'<[^>]*(error|validation|invalid)[^>]*>', html, re.IGNORECASE)

        if error_elements:
            return f"ℹ️  Found {len(error_elements)} error/feedback elements"
        return None

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
