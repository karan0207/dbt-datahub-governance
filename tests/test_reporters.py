"""Tests for reporters."""

import json
import pytest
from pathlib import Path

from src.models.dbt_models import dbtModel, NodeType, MaterializationType
from src.models.governance import (
    RuleType,
    SeverityLevel,
    Violation,
)
from src.reporters import get_reporter, list_reporters
from src.reporters.json_reporter import JSONReporter
from src.reporters.markdown import MarkdownReporter
from src.reporters.github import GitHubReporter


@pytest.fixture
def violations():
    """Create sample violations for testing."""
    return [
        Violation(
            rule_name="require_owner",
            rule_type=RuleType.OWNERSHIP,
            severity=SeverityLevel.ERROR,
            model_name="stg_orders",
            model_unique_id="model.test.stg_orders",
            message="Model has no owners defined",
            details={"required_ownership_types": ["DataOwner"]},
        ),
        Violation(
            rule_name="require_description",
            rule_type=RuleType.DOCUMENTATION,
            severity=SeverityLevel.WARNING,
            model_name="stg_orders",
            model_unique_id="model.test.stg_orders",
            message="Model description is too short",
            details={"current_length": 5, "required_length": 10},
        ),
        Violation(
            rule_name="require_pii_tag",
            rule_type=RuleType.TAG,
            severity=SeverityLevel.ERROR,
            model_name="stg_customers",
            model_unique_id="model.test.stg_customers",
            message="Model is missing required tag: pii",
            details={"required_tags": ["pii"]},
        ),
    ]


@pytest.fixture
def models():
    """Create sample models for testing."""
    return [
        dbtModel(
            name="stg_orders",
            unique_id="model.test.stg_orders",
            resource_type=NodeType.MODEL,
            package_name="test",
            path="models/staging/stg_orders.sql",
            original_file_path="models/staging/stg_orders.sql",
            description="Short",
            columns={},
            meta={},
            tags=[],
            depends_on={"nodes": []},
            config={},
            schema_="analytics",
        ),
        dbtModel(
            name="stg_customers",
            unique_id="model.test.stg_customers",
            resource_type=NodeType.MODEL,
            package_name="test",
            path="models/staging/stg_customers.sql",
            original_file_path="models/staging/stg_customers.sql",
            description="",
            columns={},
            meta={},
            tags=[],
            depends_on={"nodes": []},
            config={},
            schema_="analytics",
        ),
        dbtModel(
            name="fct_orders",
            unique_id="model.test.fct_orders",
            resource_type=NodeType.MODEL,
            package_name="test",
            path="models/fct/fct_orders.sql",
            original_file_path="models/fct/fct_orders.sql",
            description="This is a complete orders fact table with all necessary information",
            columns={},
            meta={},
            tags=["core", "verified"],
            depends_on={"nodes": ["model.test.stg_orders"]},
            config={},
            schema_="analytics",
            owners=["data-team@company.com"],
            tests=[{"test_name": "unique"}, {"test_name": "not_null"}],
        ),
    ]


class TestJSONReporter:
    """Tests for JSONReporter."""

    def test_generate_report(self, violations, models, tmp_path):
        """Test generating a JSON report."""
        reporter = JSONReporter()
        output_file = tmp_path / "report.json"

        report = reporter.generate_report(violations, models, output_path=output_file)

        assert isinstance(report, str)
        data = json.loads(report)
        assert "report" in data
        assert "summary" in data["report"]
        assert "results" in data["report"]
        assert output_file.exists()

    def test_report_summary(self, violations, models):
        """Test report summary in JSON."""
        reporter = JSONReporter()
        report = reporter.generate_report(violations, models)

        data = json.loads(report)
        summary = data["report"]["summary"]

        assert summary["total_models"] == 3
        assert summary["failed_models"] == 2
        assert summary["total_violations"] == 3
        assert summary["severity_counts"]["error"] == 2
        assert summary["severity_counts"]["warning"] == 1

    def test_report_results(self, violations, models):
        """Test report results section."""
        reporter = JSONReporter()
        report = reporter.generate_report(violations, models)

        data = json.loads(report)
        results = data["report"]["results"]

        assert len(results) == 3
        stg_orders_result = next(r for r in results if r["model"] == "stg_orders")
        assert stg_orders_result["status"] == "failed"
        assert stg_orders_result["violation_count"] == 2


class TestMarkdownReporter:
    """Tests for MarkdownReporter."""

    def test_generate_report(self, violations, models, tmp_path):
        """Test generating a Markdown report."""
        reporter = MarkdownReporter()
        output_file = tmp_path / "report.md"

        report = reporter.generate_report(violations, models, output_path=output_file)

        assert isinstance(report, str)
        assert "# Data Governance Report" in report
        assert "## Summary" in report
        assert "## Violations" in report
        assert output_file.exists()

    def test_report_contains_tables(self, violations, models):
        """Test that report contains properly formatted tables."""
        reporter = MarkdownReporter()
        report = reporter.generate_report(violations, models)

        assert "| Model | Severity | Rule | Message |" in report
        assert "|-------|----------|------|---------|" in report

    def test_report_passed_models(self, violations, models):
        """Test that passed models are included in report."""
        reporter = MarkdownReporter()
        report = reporter.generate_report(violations, models)

        assert "## Passed Models" in report
        assert "fct_orders" in report


class TestGitHubReporter:
    """Tests for GitHubReporter."""

    def test_generate_report(self, violations, models):
        """Test generating a GitHub comment report."""
        reporter = GitHubReporter()
        report = reporter.generate_report(violations, models)

        assert isinstance(report, str)
        assert "## Data Governance Check Results" in report
        assert "❌" in report or "⚠️" in report

    def test_report_status_icon(self, violations, models):
        """Test that status icon reflects violation severity."""
        reporter = GitHubReporter()
        report = reporter.generate_report(violations, models)

        assert "❌" in report
        assert "Governance checks failed" in report

    def test_report_violations_table(self, violations, models):
        """Test that violations are shown in a table."""
        reporter = GitHubReporter()
        report = reporter.generate_report(violations, models)

        assert "| Model | Severity | Rule | Message |" in report
        assert "stg_orders" in report
        assert "stg_customers" in report

    def test_report_passed_models(self, violations, models):
        """Test that passed models are listed."""
        reporter = GitHubReporter()
        report = reporter.generate_report(violations, models)

        assert "✅ The following models have no governance violations" in report
        assert "fct_orders" in report


class TestReporterFactory:
    """Tests for reporter factory functions."""

    def test_get_reporter_console(self):
        """Test getting console reporter."""
        from src.reporters.console import ConsoleReporter

        reporter = get_reporter("console")
        assert isinstance(reporter, ConsoleReporter)

    def test_get_reporter_json(self):
        """Test getting JSON reporter."""
        reporter = get_reporter("json")
        assert isinstance(reporter, JSONReporter)

    def test_get_reporter_markdown(self):
        """Test getting Markdown reporter."""
        reporter = get_reporter("markdown")
        assert isinstance(reporter, MarkdownReporter)

    def test_get_reporter_github(self):
        """Test getting GitHub reporter."""
        reporter = get_reporter("github")
        assert isinstance(reporter, GitHubReporter)

    def test_get_reporter_invalid(self):
        """Test getting invalid reporter type."""
        with pytest.raises(ValueError) as exc_info:
            get_reporter("invalid")

        assert "Unsupported reporter type" in str(exc_info.value)

    def test_list_reporters(self):
        """Test listing all available reporters."""
        reporters = list_reporters()

        assert "console" in reporters
        assert "json" in reporters
        assert "markdown" in reporters
        assert "github" in reporters
