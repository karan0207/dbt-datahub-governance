"""Tests for rules engine."""

import pytest
from src.models.dbt_models import dbtModel, NodeType, MaterializationType
from src.models.governance import (
    GovernanceConfig,
    GovernanceRule,
    RuleConfig,
    RuleType,
    SeverityLevel,
    Violation,
)
from src.rules.engine import RulesEngine
from src.rules.builtin import (
    OwnershipRule,
    DocumentationRule,
    TagRule,
    ColumnRule,
    TestRule,
)


class TestRulesEngine:
    """Tests for RulesEngine class."""

    def test_evaluate_no_rules(self, sample_model):
        """Test evaluation with no rules."""
        engine = RulesEngine(rules=[])
        violations = engine.evaluate([sample_model])

        assert len(violations) == 0

    def test_evaluate_ownership_rule_pass(self, sample_model):
        """Test ownership rule that passes."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                    config=RuleConfig(required_ownership_types=["DataOwner"]),
                )
            ]
        )
        violations = engine.evaluate([sample_model])

        assert len(violations) == 0

    def test_evaluate_ownership_rule_fail(self, sample_model_no_owner):
        """Test ownership rule that fails."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                    config=RuleConfig(required_ownership_types=["DataOwner"]),
                )
            ]
        )
        violations = engine.evaluate([sample_model_no_owner])

        assert len(violations) == 1
        assert violations[0].rule_name == "require_owner"
        assert violations[0].severity == SeverityLevel.ERROR

    def test_evaluate_documentation_rule(self, sample_model):
        """Test documentation rule."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_description",
                    type=RuleType.DOCUMENTATION,
                    severity=SeverityLevel.WARNING,
                    config=RuleConfig(required_description_length=100),
                )
            ]
        )
        violations = engine.evaluate([sample_model])

        assert len(violations) == 1
        assert violations[0].rule_name == "require_description"

    def test_evaluate_tag_rule(self, sample_model):
        """Test tag rule."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_pii_tag",
                    type=RuleType.TAG,
                    severity=SeverityLevel.ERROR,
                    config=RuleConfig(required_tags=["pii"]),
                )
            ]
        )
        violations = engine.evaluate([sample_model])

        assert len(violations) == 1
        assert "pii" in violations[0].message

    def test_evaluate_column_rule(self, sample_model):
        """Test column rule."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_audit_columns",
                    type=RuleType.COLUMN,
                    severity=SeverityLevel.ERROR,
                    config=RuleConfig(required_columns=["created_at", "updated_at"]),
                )
            ]
        )
        violations = engine.evaluate([sample_model])

        assert len(violations) >= 1
        assert any("created_at" in v.message for v in violations)

    def test_evaluate_test_rule(self, sample_model):
        """Test test rule."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_tests",
                    type=RuleType.TEST,
                    severity=SeverityLevel.WARNING,
                    config=RuleConfig(test_coverage_min=5),
                )
            ]
        )
        violations = engine.evaluate([sample_model])

        assert len(violations) == 1
        assert "test_coverage_min" in violations[0].message

    def test_evaluate_with_excluded_models(self, sample_model, sample_model_no_owner):
        """Test evaluation with excluded models."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                )
            ],
            excluded_models=["stg_customers"],
        )
        violations = engine.evaluate([sample_model, sample_model_no_owner])

        assert len(violations) == 0
        assert sample_model_no_owner.name not in [v.model_name for v in violations]

    def test_evaluate_with_included_models(self, sample_model, sample_model_no_owner):
        """Test evaluation with included models."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                )
            ],
            included_models=["stg_customers"],
        )
        violations = engine.evaluate([sample_model, sample_model_no_owner])

        assert len(violations) == 1
        assert violations[0].model_name == "stg_customers"

    def test_evaluate_multiple_rules(self, sample_model_no_owner):
        """Test evaluation with multiple rules."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                ),
                GovernanceRule(
                    name="require_description",
                    type=RuleType.DOCUMENTATION,
                    severity=SeverityLevel.WARNING,
                ),
            ]
        )
        violations = engine.evaluate([sample_model_no_owner])

        assert len(violations) == 2
        rule_names = [v.rule_name for v in violations]
        assert "require_owner" in rule_names
        assert "require_description" in rule_names

    def test_evaluate_with_results(self, sample_model_no_owner):
        """Test evaluation with detailed results."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                ),
                GovernanceRule(
                    name="require_description",
                    type=RuleType.DOCUMENTATION,
                    severity=SeverityLevel.WARNING,
                ),
            ]
        )
        result = engine.evaluate_with_results([sample_model_no_owner])

        assert result.total_models == 1
        assert result.passed_models == 0
        assert result.failed_models == 1
        assert result.total_violations == 2
        assert result.error_count == 1
        assert result.warning_count == 1
        assert result.info_count == 0

    def test_compile_rules(self):
        """Test rule compilation."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                ),
            ]
        )
        engine.compile_rules()

        assert len(engine._compiled_rules) == 1
        assert engine._compiled_rules[0].name == "require_owner"

    def test_disabled_rules_not_compiled(self):
        """Test that disabled rules are not compiled."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                    enabled=False,
                ),
            ]
        )
        engine.compile_rules()

        assert len(engine._compiled_rules) == 0

    def test_get_violations_by_model(self, sample_model, sample_model_no_owner):
        """Test filtering violations by model."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                ),
            ]
        )
        all_violations = engine.evaluate([sample_model, sample_model_no_owner])
        model_violations = engine.get_violations_by_model(
            "stg_customers", all_violations
        )

        assert len(model_violations) == 1
        assert model_violations[0].model_name == "stg_customers"

    def test_get_violations_by_severity(self, sample_model_no_owner):
        """Test filtering violations by severity."""
        engine = RulesEngine(
            rules=[
                GovernanceRule(
                    name="require_owner",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.ERROR,
                ),
                GovernanceRule(
                    name="require_description",
                    type=RuleType.DOCUMENTATION,
                    severity=SeverityLevel.WARNING,
                ),
            ]
        )
        all_violations = engine.evaluate([sample_model_no_owner])

        errors = engine.get_violations_by_severity(SeverityLevel.ERROR, all_violations)
        warnings = engine.get_violations_by_severity(
            SeverityLevel.WARNING, all_violations
        )

        assert len(errors) == 1
        assert len(warnings) == 1
