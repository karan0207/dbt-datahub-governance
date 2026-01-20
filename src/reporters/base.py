"""Base reporter class for output formatting."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import Violation


class BaseReporter(ABC):
    """Abstract base class for reporters."""

    def __init__(self):
        """Initialize reporter."""
        pass

    @abstractmethod
    def generate_report(
        self,
        violations: List[Violation],
        models: List[dbtModel],
        output_path: Optional[Path] = None,
    ) -> str:
        """Generate a report from violations.

        Args:
            violations: List of governance violations.
            models: List of dbt models.
            output_path: Optional path to write report file.

        Returns:
            Report string.
        """
        pass

    def _group_violations_by_model(
        self,
        violations: List[Violation],
    ) -> Dict[str, List[Violation]]:
        """Group violations by model name.

        Args:
            violations: List of violations.

        Returns:
            Dictionary mapping model names to violations.
        """
        grouped = {}
        for violation in violations:
            if violation.model_name not in grouped:
                grouped[violation.model_name] = []
            grouped[violation.model_name].append(violation)
        return grouped

    def _count_by_severity(
        self,
        violations: List[Violation],
    ) -> Dict[str, int]:
        """Count violations by severity.

        Args:
            violations: List of violations.

        Returns:
            Dictionary mapping severity to count.
        """
        counts = {"error": 0, "warning": 0, "info": 0}
        for v in violations:
            counts[v.severity.value] += 1
        return counts
