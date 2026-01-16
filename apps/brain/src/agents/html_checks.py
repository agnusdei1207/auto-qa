"""
HTML Checks - Individual HTML validation functions

Provides focused functions for checking:
- Accessibility (alt tags, ARIA labels, form labels)
- Structure (valid HTML, proper nesting)
- Semantics (semantic HTML tags)
- Forms (validation, labels, error messages)
"""
import re
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class HTMLChecks:
    """HTML validation and analysis utilities"""

    def check_images_have_alt(self, html: str) -> Optional[str]:
        """Check if all images have alt attributes"""
        images = re.findall(r'<img[^>]+>', html, re.IGNORECASE)
        no_alt = [img for img in images if 'alt=' not in img.lower()]

        if no_alt:
            return f"⚠️  {len(no_alt)} images missing alt attribute"
        return None

    def check_forms_have_labels(self, html: str) -> Optional[str]:
        """Check if form inputs have labels"""
        inputs = re.findall(r'<input[^>]+>', html, re.IGNORECASE)
        unlabeled = [inp for inp in inputs if 'id=' in inp.lower()]

        if unlabeled:
            return f"⚠️  {len(unlabeled)} inputs may lack labels"
        return None

    def check_heading_hierarchy(self, html: str) -> Optional[str]:
        """Check heading hierarchy"""
        headings = re.findall(r'<h([1-6])', html, re.IGNORECASE)

        if not headings:
            return None

        if headings[0] != '1':
            return f"⚠️  First heading is H{headings[0]}, should be H1"

        return None

    def check_aria_labels(self, html: str) -> Optional[str]:
        """Check ARIA labels for interactive elements"""
        buttons = re.findall(r'<button[^>]*>(.*?)</button>', html, re.IGNORECASE)
        no_aria = [
            btn for btn in buttons
            if 'aria-label=' not in btn.lower()
            and not any(w in btn.lower() for w in ['>', 'icon', 'btn', '×'])
        ]

        if no_aria:
            return f"⚠️  {len(no_aria)} buttons may need aria-label"
        return None

    def find_unclosed_tags(self, html: str) -> List[str]:
        """Find potentially unclosed HTML tags"""
        common_tags = ['div', 'span', 'p', 'a', 'li']
        unclosed = []

        for tag in common_tags:
            opens = html.count(f'<{tag}')
            closes = html.count(f'</{tag}>')

            if opens > closes:
                unclosed.append(tag)

        return unclosed

    def check_form_required_attributes(self, html: str) -> Optional[str]:
        """Check if required form fields are marked"""
        required_fields = re.findall(r'<input[^>]*required[^>]*>', html, re.IGNORECASE)

        if not required_fields:
            return None

        return f"ℹ️  Found {len(required_fields)} required form fields"

    def check_form_input_types(self, html: str) -> Optional[str]:
        """Check form input types"""
        email_inputs = re.findall(r'<input[^>]*type=["\']?email["\']?[^>]*>', html, re.IGNORECASE)
        password_inputs = re.findall(r'<input[^>]*type=["\']?password["\']?[^>]*>', html, re.IGNORECASE)

        issues = []
        if email_inputs and 'type="email"' not in str(email_inputs):
            issues.append("Email field should use type=\"email\"")
        if password_inputs and 'type="password"' not in str(password_inputs):
            issues.append("Password field should use type=\"password\"")

        return "\n".join(issues) if issues else None

    def check_form_error_handling(self, html: str) -> Optional[str]:
        """Check for form error handling"""
        error_elements = re.findall(r'<[^>]*(error|validation|invalid)[^>]*>', html, re.IGNORECASE)

        if error_elements:
            return f"ℹ️  Found {len(error_elements)} error/feedback elements"
        return None

    def check_critical_issues(self, html: str) -> List[str]:
        """Check for critical HTML issues"""
        issues = []

        if not html.strip():
            issues.append("Empty HTML content")

        if "<script>" in html.lower() and "javascript:" in html.lower():
            issues.append("Inline JavaScript detected - potential security risk")

        return issues

    def check_warnings(self, html: str) -> List[str]:
        """Check for HTML warnings"""
        warnings = []

        if html.count("<div>") > 50:
            warnings.append(f"High <div> count ({html.count('<div>')}) - may indicate layout complexity")

        if len(html) > 200000:
            warnings.append(f"Large HTML ({len(html)} chars) - consider optimization")

        return warnings

    def check_info(self, html: str) -> List[str]:
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

    def check_semantic_tags(self, html: str) -> List[str]:
        """Check for semantic HTML tags"""
        semantic_tags = [
            "header", "nav", "main", "article", "section",
            "aside", "footer", "figure", "figcaption"
        ]

        if not any(tag in html for tag in semantic_tags):
            return ["No semantic HTML tags found"]

        return []

    def check_div_usage(self, html: str) -> List[str]:
        """Check for excessive div usage"""
        issues = []

        if "<div>" in html and "<span>" in html:
            div_count = html.count("<div>")
            issues.append(f"High <div> usage ({div_count} instances) - consider semantic tags")

        return issues

    def check_heading_structure(self, html: str) -> List[str]:
        """Check heading structure"""
        issues = []

        heading_structure = re.findall(r'<h([1-6])>', html)
        if heading_structure:
            if heading_structure[0] != '1':
                issues.append(f"First heading is H{heading_structure[0]}, should be H1")

        return issues
