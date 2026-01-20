"""Markdown reporter for documentation."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import SeverityLevel, Violation
from .base import BaseReporter


class MarkdownReporter(BaseReporter):
    """Reporter that outputs Markdown format."""

    def generate_report(
        self,
        violations: List[Violation],
        models: List[dbtModel],
        output_path: Optional[Path] = None,
    ) -> str:
        """Generate a Markdown report.

        Args:
            violations: List of governance violations.
            models: List of dbt models.
            output_path: Optional path to write Markdown file.

        Returns:
            Markdown string.
        """
        grouped = self._group_violations_by_model(violations)
        model_names = [m.name for m in models]
        passed_models = set(model_names) - set(grouped.keys())
        severity_counts = self._count_by_severity(violations)

        lines = [
            "# Data Governance Report",
            f"\n**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Models | {len(models)} |",
            f"| Passed | {len(passed_models)} |",
            f"| Failed | {len(grouped)} |",
            f"| Total Violations | {len(violations)} |",
            f"| Errors | {severity_counts['error']} |",
            f"| Warnings | {severity_counts['warning']} |",
            f"| Info | {severity_counts['info']} |",
            "",
        ]

        if violations:
            lines.extend(
                [
                    "## Violations",
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
                    icon = (
                        "❌"
                        if severity == "ERROR"
                        else "⚠️"
                        if severity == "WARNING"
                        else "ℹ️"
                    )
                    lines.append(
                        f"| {model_name} | {icon} {severity} | {violation.rule_name} | {violation.message} |"
                    )

            lines.append("")

        if passed_models:
            lines.extend(
                [
                    "## Passed Models",
                    "",
                    "Models with no governance violations:",
                    "",
                ]
            )
            for model_name in sorted(passed_models):
                lines.append(f"- {model_name}")
            lines.append("")

        markdown_output = "\n".join(lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(markdown_output)

        return markdown_output
