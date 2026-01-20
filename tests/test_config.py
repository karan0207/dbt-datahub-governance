"""Tests for configuration loader."""

import pytest
from pathlib import Path

from src.config.loader import ConfigLoader
from src.models.governance import (
    GovernanceConfig,
    GovernanceRule,
    RuleConfig,
    RuleType,
    SeverityLevel,
)


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_load_basic_config(self, temp_config_file):
        """Test loading a basic configuration file."""
        loader = ConfigLoader()
        config = loader.load(temp_config_file)

        assert len(config.rules) == 2
        assert config.excluded_models == ["stg__tmp_*"]

    def test_load_default_config(self):
        """Test loading default configuration."""
        loader = ConfigLoader()
        config = loader.load_default()

        assert len(config.rules) > 0
        assert config.excluded_models == []
        assert config.included_models == []

    def test_parse_rule_ownership(self):
        """Test parsing an ownership rule."""
        loader = ConfigLoader()
        rule_data = {
            "name": "require_owner",
            "type": "ownership",
            "severity": "error",
            "description": "Models must have owners",
            "config": {
                "required_ownership_types": ["DataOwner", "TechnicalOwner"],
            },
        }

        rule = loader._parse_rule(rule_data)

        assert rule is not None
        assert rule.name == "require_owner"
        assert rule.type == RuleType.OWNERSHIP
        assert rule.severity == SeverityLevel.ERROR
        assert "DataOwner" in rule.config.required_ownership_types
        assert "TechnicalOwner" in rule.config.required_ownership_types

    def test_parse_rule_documentation(self):
        """Test parsing a documentation rule."""
        loader = ConfigLoader()
        rule_data = {
            "name": "require_description",
            "type": "documentation",
            "severity": "warning",
            "config": {
                "required_description_length": 50,
            },
        }

        rule = loader._parse_rule(rule_data)

        assert rule is not None
        assert rule.type == RuleType.DOCUMENTATION
        assert rule.config.required_description_length == 50

    def test_parse_rule_column(self):
        """Test parsing a column rule."""
        loader = ConfigLoader()
        rule_data = {
            "name": "require_columns",
            "type": "column",
            "severity": "error",
            "config": {
                "required_columns": ["created_at", "updated_at"],
                "column_descriptions_required": True,
            },
        }

        rule = loader._parse_rule(rule_data)

        assert rule is not None
        assert rule.type == RuleType.COLUMN
        assert "created_at" in rule.config.required_columns
        assert "updated_at" in rule.config.required_columns
        assert rule.config.column_descriptions_required is True

    def test_generate_basic_example(self):
        """Test generating a basic example configuration."""
        loader = ConfigLoader()
        example = loader.generate_example("basic")

        assert "rules" in example
        assert len(example["rules"]) == 2

    def test_generate_full_example(self):
        """Test generating a full example configuration."""
        loader = ConfigLoader()
        example = loader.generate_example("full")

        assert "rules" in example
        assert len(example["rules"]) > 2
        assert "excluded_models" in example
        assert "datahub" in example

    def test_load_invalid_file(self):
        """Test loading a non-existent file."""
        loader = ConfigLoader()

        with pytest.raises(FileNotFoundError):
            loader.load("/nonexistent/path/config.yml")

    def test_load_empty_config(self, tmp_path):
        """Test loading an empty configuration file."""
        config_file = tmp_path / "empty.yml"
        config_file.write_text("")

        loader = ConfigLoader()
        config = loader.load(config_file)

        assert len(config.rules) == 0

    def test_save_and_load_config(self, tmp_path):
        """Test saving and loading a configuration."""
        loader = ConfigLoader()

        original_config = GovernanceConfig(
            rules=[
                GovernanceRule(
                    name="test_rule",
                    type=RuleType.TAG,
                    severity=SeverityLevel.INFO,
                    config=RuleConfig(required_tags=["tag1"]),
                )
            ]
        )

        output_file = tmp_path / "saved_config.yml"
        loader.save(original_config, output_file)

        loaded_config = loader.load(output_file)

        assert len(loaded_config.rules) == 1
        assert loaded_config.rules[0].name == "test_rule"
