"""JSON reporter for machine-readable output."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import Violation
from .base import BaseReporter


class JSONReporter(BaseReporter):
    """Reporter that outputs JSON format."""

    def generate_report(
        self,
        violations: List[Violation],
        models: List[dbtModel],
        output_path: Optional[Path] = None,
    ) -> str:
        """Generate a JSON report.

        Args:
            violations: List of governance violations.
            models: List of dbt models.
            output_path: Optional path to write JSON file.

        Returns:
            JSON string.
        """
        report = self._build_report(violations, models)

        json_output = json.dumps(report, indent=2, default=str)

        if output_path:
            with open(output_path, "w") as f:
                f.write(json_output)

        return json_output

    def _build_report(
        self,
        violations: List[Violation],
        models: List[dbtModel],
    ) -> Dict[str, Any]:
        """Build report dictionary.

        Args:
            violations: List of governance violations.
            models: List of dbt models.

        Returns:
            Report dictionary.
        """
        grouped = self._group_violations_by_model(violations)
        model_names = [m.name for m in models]
        passed_models = set(model_names) - set(grouped.keys())
        severity_counts = self._count_by_severity(violations)

        report = {
            "report": {
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_models": len(models),
                    "passed_models": len(passed_models),
                    "failed_models": len(grouped),
                    "total_violations": len(violations),
                    "severity_counts": severity_counts,
                },
            },
            "results": [],
        }

        for model_name in sorted(grouped.keys()):
            model_violations = grouped[model_name]
            error_count = sum(
                1 for v in model_violations if v.severity.value == "error"
            )
            warning_count = sum(
                1 for v in model_violations if v.severity.value == "warning"
            )
            info_count = sum(1 for v in model_violations if v.severity.value == "info")

            result = {
                "model": model_name,
                "status": "failed" if model_violations else "passed",
                "violation_count": len(model_violations),
                "severity_counts": {
                    "error": error_count,
                    "warning": warning_count,
                    "info": info_count,
                },
                "violations": [
                    {
                        "rule": v.rule_name,
                        "type": v.rule_type.value,
                        "severity": v.severity.value,
                        "message": v.message,
                        "details": v.details,
                    }
                    for v in model_violations
                ],
            }
            report["results"].append(result)

        for model_name in sorted(passed_models):
            report["results"].append(
                {
                    "model": model_name,
                    "status": "passed",
                    "violation_count": 0,
                    "severity_counts": {"error": 0, "warning": 0, "info": 0},
                    "violations": [],
                }
            )

        return report
