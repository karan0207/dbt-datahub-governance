"""GitHub comment reporter for PR feedback."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import SeverityLevel, Violation
from .base import BaseReporter


class GitHubReporter(BaseReporter):
    """Reporter that outputs GitHub-flavored comment format."""

    def generate_report(
        self,
        violations: List[Violation],
        models: List[dbtModel],
        output_path: Optional[Path] = None,
    ) -> str:
        """Generate a GitHub comment report.

        Args:
            violations: List of governance violations.
            models: List of dbt models.
            output_path: Ignored for GitHub reporter.

        Returns:
            GitHub-flavored Markdown string for comments.
        """
        grouped = self._group_violations_by_model(violations)
        model_names = [m.name for m in models]
        passed_models = set(model_names) - set(grouped.keys())
        severity_counts = self._count_by_severity(violations)

        has_errors = severity_counts["error"] > 0
        has_warnings = severity_counts["warning"] > 0

        status_icon = "✅" if not violations else "❌" if has_errors else "⚠️"
        status_text = (
            "All checks passed"
            if not violations
            else "Governance checks failed"
            if has_errors
            else "Governance checks passed with warnings"
        )

        lines = [
            f"## Data Governance Check Results {status_icon}",
            "",
            f"**Status:** {status_text}",
            "",
            "### Summary",
            "",
            f"- **Total Models:** {len(models)}",
            f"- **Passed:** {len(passed_models)}",
            f"- **Failed:** {len(grouped)}",
            f"- **Errors:** {severity_counts['error']} {self._severity_icon('error')}",
            f"- **Warnings:** {severity_counts['warning']} {self._severity_icon('warning')}",
            f"- **Info:** {severity_counts['info']} {self._severity_icon('info')}",
            "",
        ]

        if violations:
            lines.extend(
                [
                    "### Violations",
                    "",
                    "<details>",
                    "<summary>View details</summary>",
                    "",
                    "| Model | Severity | Rule | Message |",
                    "|-------|----------|------|---------|",
                ]
            )

            for model_name in sorted(grouped.keys()):
                model_violations = grouped[model_name]
                for violation in sorted(
                    model_violations, key=lambda v: (v.severity.value, v.rule_name)
                ):
                    severity = violation.severity.value.upper()
                    icon = self._severity_icon(violation.severity.value)
                    lines.append(
                        f"| `{model_name}` | {icon} {severity} | `{violation.rule_name}` | {violation.message} |"
                    )

            lines.extend(
                [
                    "",
                    "</details>",
                    "",
                ]
            )

        if passed_models:
            lines.extend(
                [
                    "### Passed Models",
                    "",
                    "✅ The following models have no governance violations:",
                    "",
                ]
            )
            for model_name in sorted(passed_models):
                lines.append(f"- `{model_name}`")
            lines.append("")

        lines.extend(
            [
                "",
                "---",
                f"*Report generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}*",
            ]
        )

        return "\n".join(lines)

    def _severity_icon(self, severity: str) -> str:
        """Get icon for severity level.

        Args:
            severity: Severity level string.

        Returns:
            Icon string.
        """
        icons = {
            "error": "🔴",
            "warning": "🟡",
            "info": "🟢",
        }
        return icons.get(severity, "⚪")
