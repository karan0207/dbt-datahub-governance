"""Console reporter for terminal output."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import SeverityLevel, Violation
from .base import BaseReporter


class ConsoleReporter(BaseReporter):
    """Reporter that outputs to console with rich formatting."""

    ICONS = {
        "error": "✗",
        "warning": "⚠",
        "info": "✓",
    }

    COLORS = {
        "error": "red",
        "warning": "yellow",
        "info": "green",
    }

    def generate_report(
        self,
        violations: List[Violation],
        models: List[dbtModel],
        output_path: Optional[Path] = None,
    ) -> str:
        """Generate a console report.

        Args:
            violations: List of governance violations.
            models: List of dbt models.
            output_path: Ignored for console reporter.

        Returns:
            Report string (will be printed directly).
        """
        from rich import box
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text

        console = Console()

        grouped = self._group_violations_by_model(violations)
        model_names = {m.name for m in models}
        passed_models = model_names - set(grouped.keys())
        severity_counts = self._count_by_severity(violations)

        console.print("\n[bold]Data Governance Report[/bold]\n")

        summary_table = Table(box=box.SIMPLE, show_header=False)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Total Models", str(len(models)))
        summary_table.add_row("Passed", str(len(passed_models)))
        summary_table.add_row("Failed", str(len(grouped)))
        summary_table.add_row(
            "Errors",
            Text(str(severity_counts["error"]), style="red"),
        )
        summary_table.add_row(
            "Warnings",
            Text(str(severity_counts["warning"]), style="yellow"),
        )
        summary_table.add_row(
            "Info",
            Text(str(severity_counts["info"]), style="green"),
        )

        console.print(summary_table)

        if violations:
            console.print("\n[bold]Violations:[/bold]\n")

            for model_name in sorted(grouped.keys()):
                model_violations = grouped[model_name]
                has_error = any(
                    v.severity == SeverityLevel.ERROR for v in model_violations
                )
                status_icon = (
                    self.ICONS["error"] if has_error else self.ICONS["warning"]
                )
                status_color = (
                    self.COLORS["error"] if has_error else self.COLORS["warning"]
                )

                console.print(
                    f"{status_icon} [bold][{status_color}]{model_name}[/bold]"
                )

                for violation in sorted(
                    model_violations, key=lambda v: (v.severity.value, v.rule_name)
                ):
                    severity = violation.severity.value
                    icon = self.ICONS.get(severity, "•")
                    color = self.COLORS.get(severity, "white")

                    console.print(
                        f"  {icon} [{color}]{violation.rule_name}[/]: {violation.message}"
                    )

                console.print()

        if passed_models:
            console.print("[green]✓ Models with no violations:[/green]")
            for model_name in sorted(passed_models):
                console.print(f"  - {model_name}")
            console.print()

        return ""
