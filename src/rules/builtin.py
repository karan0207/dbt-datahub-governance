"""Built-in governance rules for dbt models."""

import fnmatch
from typing import Any, Dict, List, Optional

from ..models.dbt_models import dbtModel
from ..models.governance import RuleType, SeverityLevel, Violation
from .base import BaseRule


class OwnershipRule(BaseRule):
    """Rule that validates model ownership."""

    def __init__(
        self,
        name: str = "require_ownership",
        severity: SeverityLevel = SeverityLevel.WARNING,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize ownership rule.

        Args:
            name: Rule name.
            severity: Severity level.
            config: Rule configuration.
        """
        super().__init__(
            name=name,
            rule_type=RuleType.OWNERSHIP,
            severity=severity,
            description="Ensure models have required ownership types",
            config=config,
        )

    def evaluate(
        self,
        model: dbtModel,
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate model ownership.

        Args:
            model: dbtModel to evaluate.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations.
        """
        violations = []

        ownership_types = self.config.get("required_ownership_types", [])
        model_owners = model.owners

        if datahub_context:
            urn = datahub_context.get("urn_mapper", {}).get(model.name)
            if urn:
                datahub_owners = datahub_context.get("ownership", {}).get(urn, [])
                model_owners = model_owners + datahub_owners

        if not model_owners:
            violations.append(
                self.create_violation(
                    model,
                    f"Model has no owners defined",
                    {"required_ownership_types": ownership_types},
                )
            )
        elif ownership_types:
            has_required = any(owner in model_owners for owner in ownership_types)
            if not has_required:
                violations.append(
                    self.create_violation(
                        model,
                        f"Model owners {model_owners} do not include required types: {ownership_types}",
                        {
                            "current_owners": model_owners,
                            "required_ownership_types": ownership_types,
                        },
                    )
                )

        return violations


class DocumentationRule(BaseRule):
    """Rule that validates model documentation."""

    def __init__(
        self,
        name: str = "require_description",
        severity: SeverityLevel = SeverityLevel.WARNING,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize documentation rule.

        Args:
            name: Rule name.
            severity: Severity level.
            config: Rule configuration.
        """
        super().__init__(
            name=name,
            rule_type=RuleType.DOCUMENTATION,
            severity=severity,
            description="Ensure models have descriptions",
            config=config,
        )

    def evaluate(
        self,
        model: dbtModel,
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate model documentation.

        Args:
            model: dbtModel to evaluate.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations.
        """
        violations = []

        description = model.description
        min_length = self.config.get("required_description_length", 0)

        if datahub_context and not description:
            urn = datahub_context.get("urn_mapper", {}).get(model.name)
            if urn:
                description = datahub_context.get("descriptions", {}).get(urn, "")

        if not description:
            violations.append(
                self.create_violation(
                    model,
                    "Model has no description",
                    {"required_length": min_length},
                )
            )
        elif min_length > 0 and len(description) < min_length:
            violations.append(
                self.create_violation(
                    model,
                    f"Model description is too short ({len(description)} < {min_length} characters)",
                    {
                        "current_length": len(description),
                        "required_length": min_length,
                    },
                )
            )

        return violations


class TagRule(BaseRule):
    """Rule that validates model tags."""

    def __init__(
        self,
        name: str = "validate_tags",
        severity: SeverityLevel = SeverityLevel.WARNING,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize tag rule.

        Args:
            name: Rule name.
            severity: Severity level.
            config: Rule configuration.
        """
        super().__init__(
            name=name,
            rule_type=RuleType.TAG,
            severity=severity,
            description="Validate model tags",
            config=config,
        )

    def evaluate(
        self,
        model: dbtModel,
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate model tags.

        Args:
            model: dbtModel to evaluate.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations.
        """
        violations = []

        required_tags = self.config.get("required_tags", [])
        forbidden_tags = self.config.get("forbidden_tags", [])
        model_tags = set(model.tags)

        if datahub_context:
            urn = datahub_context.get("urn_mapper", {}).get(model.name)
            if urn:
                datahub_tags = set(datahub_context.get("tags", {}).get(urn, []))
                model_tags = model_tags | datahub_tags

        for required_tag in required_tags:
            if required_tag not in model_tags:
                violations.append(
                    self.create_violation(
                        model,
                        f"Model is missing required tag: {required_tag}",
                        {
                            "required_tags": required_tags,
                            "current_tags": list(model_tags),
                        },
                    )
                )

        for forbidden_tag in forbidden_tags:
            if forbidden_tag in model_tags:
                violations.append(
                    self.create_violation(
                        model,
                        f"Model has forbidden tag: {forbidden_tag}",
                        {
                            "forbidden_tags": forbidden_tags,
                            "current_tags": list(model_tags),
                        },
                    )
                )

        return violations


class ColumnRule(BaseRule):
    """Rule that validates model columns."""

    def __init__(
        self,
        name: str = "validate_columns",
        severity: SeverityLevel = SeverityLevel.WARNING,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize column rule.

        Args:
            name: Rule name.
            severity: Severity level.
            config: Rule configuration.
        """
        super().__init__(
            name=name,
            rule_type=RuleType.COLUMN,
            severity=severity,
            description="Validate model columns",
            config=config,
        )

    def evaluate(
        self,
        model: dbtModel,
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate model columns.

        Args:
            model: dbtModel to evaluate.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations.
        """
        violations = []

        required_columns = self.config.get("required_columns", [])
        require_descriptions = self.config.get("column_descriptions_required", False)
        model_columns = model.columns

        for required_col in required_columns:
            if required_col not in model_columns:
                violations.append(
                    self.create_violation(
                        model,
                        f"Model is missing required column: {required_col}",
                        {
                            "required_columns": required_columns,
                            "current_columns": list(model_columns.keys()),
                        },
                    )
                )

        if require_descriptions:
            for col_name, col_info in model_columns.items():
                description = col_info.get("description", "")
                if not description:
                    violations.append(
                        self.create_violation(
                            model,
                            f"Column '{col_name}' has no description",
                            {
                                "column": col_name,
                                "require_descriptions": True,
                            },
                        )
                    )

        return violations


class LineageRule(BaseRule):
    """Rule that validates model lineage."""

    def __init__(
        self,
        name: str = "validate_lineage",
        severity: SeverityLevel = SeverityLevel.WARNING,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize lineage rule.

        Args:
            name: Rule name.
            severity: Severity level.
            config: Rule configuration.
        """
        super().__init__(
            name=name,
            rule_type=RuleType.LINEAGE,
            severity=severity,
            description="Validate model lineage",
            config=config,
        )

    def evaluate(
        self,
        model: dbtModel,
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate model lineage.

        Args:
            model: dbtModel to evaluate.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations.
        """
        violations = []

        required_parents = self.config.get("parent_models", [])
        if not required_parents:
            return violations

        model_depends_on = model.depends_on.get("nodes", [])

        for required_parent in required_parents:
            import fnmatch

            has_parent = any(
                fnmatch.fnmatch(dep, required_parent) for dep in model_depends_on
            )
            if not has_parent:
                violations.append(
                    self.create_violation(
                        model,
                        f"Model does not depend on required parent model: {required_parent}",
                        {
                            "required_parents": required_parents,
                            "current_parents": model_depends_on,
                        },
                    )
                )

        return violations


class TestRule(BaseRule):
    """Rule that validates model tests."""

    def __init__(
        self,
        name: str = "require_tests",
        severity: SeverityLevel = SeverityLevel.WARNING,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize test rule.

        Args:
            name: Rule name.
            severity: Severity level.
            config: Rule configuration.
        """
        super().__init__(
            name=name,
            rule_type=RuleType.TEST,
            severity=severity,
            description="Ensure models have tests",
            config=config,
        )

    def evaluate(
        self,
        model: dbtModel,
        datahub_context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """Evaluate model tests.

        Args:
            model: dbtModel to evaluate.
            datahub_context: Optional DataHub context.

        Returns:
            List of violations.
        """
        violations = []

        min_tests = self.config.get("test_coverage_min", 1)
        test_count = len(model.tests)

        if test_count < min_tests:
            violations.append(
                self.create_violation(
                    model,
                    f"Model has {test_count} test(s), but requires at least {min_tests}",
                    {
                        "current_tests": test_count,
                        "required_tests": min_tests,
                    },
                )
            )

        return violations
