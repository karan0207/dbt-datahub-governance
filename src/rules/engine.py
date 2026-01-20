"""Rules engine for governance validation."""

import time
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import (
    GovernanceConfig,
    GovernanceRule,
    RuleType,
    SeverityLevel,
    ValidationResult,
    Violation,
)
from .base import BaseRule
from .builtin import (
    ColumnRule,
    DocumentationRule,
    LineageRule,
    OwnershipRule,
    TagRule,
    TestRule,
)


class RulesEngine:
    """Engine for evaluating governance rules against dbt models."""

    RULE_CLASS_MAP = {
        RuleType.OWNERSHIP: OwnershipRule,
        RuleType.DOCUMENTATION: DocumentationRule,
        RuleType.TAG: TagRule,
        RuleType.COLUMN: ColumnRule,
        RuleType.LINEAGE: LineageRule,
        RuleType.TEST: TestRule,
    }

    def __init__(
        self,
        rules: Optional[List[GovernanceRule]] = None,
        included_models: Optional[List[str]] = None,
        excluded_models: Optional[List[str]] = None,
    ):
        """Initialize rules engine.

        Args:
            rules: List of governance rules.
            included_models: Optional list of included model patterns.
            excluded_models: Optional list of excluded model patterns.
        """
        self.rules = rules or []
        self.included_models = included_models or []
        self.excluded_models = excluded_models or []
        self._compiled_rules: List[BaseRule] = []

    def load_rules(self, config: GovernanceConfig) -> None:
        """Load rules from governance configuration.

        Args:
            config: GovernanceConfig object.
        """
        self.rules = config.rules
        self.included_models = config.included_models
        self.excluded_models = config.excluded_models

    def compile_rules(self) -> None:
        """Compile governance rules into executable rule objects."""
        self._compiled_rules = []

        for rule_def in self.rules:
            if not rule_def.enabled:
                continue

            rule_class = self.RULE_CLASS_MAP.get(rule_def.type)
            if not rule_class:
                continue

            rule = rule_class(
                name=rule_def.name,
                severity=rule_def.severity,
                config=rule_def.config.dict() if rule_def.config else None,
            )
            self._compiled_rules.append(rule)

    def evaluate(
        self,
        models: List[dbtModel],
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate all models against all rules.

        Args:
            models: List of dbtModel objects.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations found.
        """
        if not self._compiled_rules:
            self.compile_rules()

        violations = []

        for model in models:
            if not self._should_evaluate_model(model):
                continue

            for rule in self._compiled_rules:
                rule_violations = rule.evaluate(model, datahub_context)
                violations.extend(rule_violations)

        return violations

    def evaluate_with_results(
        self,
        models: List[dbtModel],
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Evaluate models and return detailed results.

        Args:
            models: List of dbtModel objects.
            datahub_context: Optional DataHub context.

        Returns:
            ValidationResult with detailed statistics.
        """
        start_time = time.time()

        violations = self.evaluate(models, datahub_context)

        duration = time.time() - start_time

        model_names = {model.name for model in models}
        violated_models = {v.model_name for v in violations}
        passed_models = model_names - violated_models

        error_count = sum(1 for v in violations if v.severity == SeverityLevel.ERROR)
        warning_count = sum(
            1 for v in violations if v.severity == SeverityLevel.WARNING
        )
        info_count = sum(1 for v in violations if v.severity == SeverityLevel.INFO)

        return ValidationResult(
            total_models=len(models),
            passed_models=len(passed_models),
            failed_models=len(violated_models),
            total_violations=len(violations),
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            violations=violations,
            duration_seconds=duration,
        )

    def _should_evaluate_model(self, model: dbtModel) -> bool:
        """Check if a model should be evaluated.

        Args:
            model: dbtModel to check.

        Returns:
            True if the model should be evaluated.
        """
        model_name = model.name

        if self.excluded_models:
            import fnmatch

            for pattern in self.excluded_models:
                if fnmatch.fnmatch(model_name, pattern):
                    return False

        if self.included_models:
            import fnmatch

            for pattern in self.included_models:
                if fnmatch.fnmatch(model_name, pattern):
                    return True
            return False

        return True

    def get_rule_by_name(self, name: str) -> Optional[BaseRule]:
        """Get a compiled rule by name.

        Args:
            name: Rule name.

        Returns:
            BaseRule object or None.
        """
        for rule in self._compiled_rules:
            if rule.name == name:
                return rule
        return None

    def get_rules_by_type(self, rule_type: RuleType) -> List[BaseRule]:
        """Get all compiled rules of a specific type.

        Args:
            rule_type: RuleType to filter by.

        Returns:
            List of matching BaseRule objects.
        """
        return [r for r in self._compiled_rules if r.rule_type == rule_type]

    def get_violations_by_model(
        self,
        model_name: str,
        violations: List[Violation],
    ) -> List[Violation]:
        """Get all violations for a specific model.

        Args:
            model_name: Name of the model.
            violations: List of all violations.

        Returns:
            List of violations for the model.
        """
        return [v for v in violations if v.model_name == model_name]

    def get_violations_by_severity(
        self,
        severity: SeverityLevel,
        violations: List[Violation],
    ) -> List[Violation]:
        """Get all violations of a specific severity.

        Args:
            severity: Severity level to filter by.
            violations: List of all violations.

        Returns:
            List of violations with the specified severity.
        """
        return [v for v in violations if v.severity == severity]
