"""Base classes for governance rules."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import RuleType, SeverityLevel, Violation


class BaseRule(ABC):
    """Abstract base class for governance rules."""

    def __init__(
        self,
        name: str,
        rule_type: RuleType,
        severity: SeverityLevel = SeverityLevel.WARNING,
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a rule.

        Args:
            name: Rule name.
            rule_type: Type of rule.
            severity: Severity level for violations.
            description: Rule description.
            config: Rule configuration dictionary.
        """
        self.name = name
        self.rule_type = rule_type
        self.severity = severity
        self.description = description
        self.config = config or {}

    @abstractmethod
    def evaluate(
        self,
        model: dbtModel,
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate a model against this rule.

        Args:
            model: dbtModel to evaluate.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations found.
        """
        pass

    def should_evaluate(
        self,
        model: dbtModel,
        included_models: Optional[List[str]] = None,
        excluded_models: Optional[List[str]] = None,
    ) -> bool:
        """Check if a model should be evaluated by this rule.

        Args:
            model: dbtModel to check.
            included_models: Optional list of included model patterns.
            excluded_models: Optional list of excluded model patterns.

        Returns:
            True if the model should be evaluated.
        """
        model_name = model.name

        if excluded_models:
            import fnmatch

            for pattern in excluded_models:
                if fnmatch.fnmatch(model_name, pattern):
                    return False

        if included_models:
            import fnmatch

            for pattern in included_models:
                if fnmatch.fnmatch(model_name, pattern):
                    return True
            return False

        return True

    def create_violation(
        self,
        model: dbtModel,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Violation:
        """Create a violation for this rule.

        Args:
            model: dbtModel that violated the rule.
            message: Violation message.
            details: Optional additional details.

        Returns:
            Violation object.
        """
        return Violation(
            rule_name=self.name,
            rule_type=self.rule_type,
            severity=self.severity,
            model_name=model.name,
            model_unique_id=model.unique_id,
            message=message,
            details=details or {},
        )
