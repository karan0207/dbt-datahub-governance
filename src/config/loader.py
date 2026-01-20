"""Configuration loader for governance rules."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from ..models.governance import (
    GovernanceConfig,
    GovernanceRule,
    RuleConfig,
    RuleType,
    SeverityLevel,
)


class ConfigLoader:
    """Load and parse governance configuration files."""

    SUPPORTED_FORMATS = (".yaml", ".yml")

    def load(self, config_path: Union[str, Path]) -> GovernanceConfig:
        """Load governance configuration from a YAML file.

        Args:
            config_path: Path to the configuration file.

        Returns:
            GovernanceConfig object with parsed rules.
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        if config_path.suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported config format: {config_path.suffix}. "
                f"Supported formats: {self.SUPPORTED_FORMATS}"
            )

        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)

        if not raw_config:
            return GovernanceConfig()

        return self._parse_config(raw_config)

    def load_default(self) -> GovernanceConfig:
        """Load default governance configuration.

        Returns:
            GovernanceConfig with basic default rules.
        """
        return GovernanceConfig(
            rules=[
                GovernanceRule(
                    name="require_description",
                    type=RuleType.DOCUMENTATION,
                    severity=SeverityLevel.WARNING,
                    description="Models should have descriptions",
                    config=RuleConfig(required_description_length=10),
                ),
                GovernanceRule(
                    name="require_ownership",
                    type=RuleType.OWNERSHIP,
                    severity=SeverityLevel.WARNING,
                    description="Models should have owners",
                ),
            ]
        )

    def load_from_string(self, config_string: str) -> GovernanceConfig:
        """Load governance configuration from a YAML string.

        Args:
            config_string: YAML configuration string.

        Returns:
            GovernanceConfig object.
        """
        raw_config = yaml.safe_load(config_string)
        if not raw_config:
            return GovernanceConfig()
        return self._parse_config(raw_config)

    def _parse_config(self, raw_config: Dict[str, Any]) -> GovernanceConfig:
        """Parse raw configuration dictionary into GovernanceConfig.

        Args:
            raw_config: Raw configuration dictionary from YAML.

        Returns:
            GovernanceConfig object.
        """
        rules = []
        for rule_data in raw_config.get("rules", []):
            rule = self._parse_rule(rule_data)
            if rule:
                rules.append(rule)

        excluded_models = raw_config.get("excluded_models", [])
        included_models = raw_config.get("included_models", [])
        datahub = raw_config.get("datahub")

        return GovernanceConfig(
            rules=rules,
            excluded_models=excluded_models,
            included_models=included_models,
            datahub=datahub,
        )

    def _parse_rule(self, rule_data: Dict[str, Any]) -> Optional[GovernanceRule]:
        """Parse a single rule from raw configuration.

        Args:
            rule_data: Raw rule configuration dictionary.

        Returns:
            GovernanceRule object or None if invalid.
        """
        if not rule_data.get("name"):
            return None

        try:
            rule_type = RuleType(rule_data.get("type", "documentation"))
        except ValueError:
            rule_type = RuleType.DOCUMENTATION

        try:
            severity = SeverityLevel(rule_data.get("severity", "warning"))
        except ValueError:
            severity = SeverityLevel.WARNING

        config_data = rule_data.get("config", {})
        config = self._parse_rule_config(config_data)

        return GovernanceRule(
            name=rule_data["name"],
            type=rule_type,
            severity=severity,
            description=rule_data.get("description", ""),
            enabled=rule_data.get("enabled", True),
            config=config,
        )

    def _parse_rule_config(self, config_data: Dict[str, Any]) -> RuleConfig:
        """Parse rule configuration.

        Args:
            config_data: Raw rule configuration dictionary.

        Returns:
            RuleConfig object.
        """
        return RuleConfig(
            required_ownership_types=config_data.get(
                "required_ownership_types",
                [],
            ),
            required_tags=config_data.get("required_tags", []),
            forbidden_tags=config_data.get("forbidden_tags", []),
            required_description_length=config_data.get(
                "required_description_length",
                0,
            ),
            required_columns=config_data.get("required_columns", []),
            column_descriptions_required=config_data.get(
                "column_descriptions_required",
                False,
            ),
            parent_models=config_data.get("parent_models", []),
            test_coverage_min=config_data.get("test_coverage_min"),
            custom_regex=config_data.get("custom_regex"),
        )

    def generate_example(self, example_type: str = "basic") -> Dict[str, Any]:
        """Generate example governance configuration.

        Args:
            example_type: Type of example to generate ('basic' or 'full').

        Returns:
            Example configuration dictionary.
        """
        if example_type == "basic":
            return self._generate_basic_example()
        return self._generate_full_example()

    def _generate_basic_example(self) -> Dict[str, Any]:
        """Generate basic example configuration.

        Returns:
            Basic example configuration dictionary.
        """
        return {
            "rules": [
                {
                    "name": "require_description",
                    "type": "documentation",
                    "severity": "warning",
                    "description": "Ensure all models have descriptions",
                    "config": {
                        "required_description_length": 10,
                    },
                },
                {
                    "name": "require_ownership",
                    "type": "ownership",
                    "severity": "error",
                    "description": "Ensure all models have owners",
                    "config": {
                        "required_ownership_types": ["DataOwner"],
                    },
                },
            ],
        }

    def _generate_full_example(self) -> Dict[str, Any]:
        """Generate full example configuration with all options.

        Returns:
            Full example configuration dictionary.
        """
        return {
            "rules": [
                {
                    "name": "require_description",
                    "type": "documentation",
                    "severity": "warning",
                    "description": "Ensure all models have descriptions",
                    "enabled": True,
                    "config": {
                        "required_description_length": 10,
                    },
                },
                {
                    "name": "require_ownership",
                    "type": "ownership",
                    "severity": "error",
                    "description": "Ensure all models have owners",
                    "enabled": True,
                    "config": {
                        "required_ownership_types": [
                            "DataOwner",
                            "TechnicalOwner",
                        ],
                    },
                },
                {
                    "name": "require_tags",
                    "type": "tag",
                    "severity": "warning",
                    "description": "Ensure critical models have PII tag",
                    "enabled": True,
                    "config": {
                        "required_tags": ["pii"],
                    },
                },
                {
                    "name": "forbid_test_tags",
                    "type": "tag",
                    "severity": "error",
                    "description": "Production models should not have test tags",
                    "enabled": True,
                    "config": {
                        "forbidden_tags": ["test", "wip"],
                    },
                },
                {
                    "name": "require_column_descriptions",
                    "type": "column",
                    "severity": "info",
                    "description": "All columns should have descriptions",
                    "enabled": True,
                    "config": {
                        "column_descriptions_required": True,
                    },
                },
                {
                    "name": "require_specific_columns",
                    "type": "column",
                    "severity": "error",
                    "description": "Critical models must have audit columns",
                    "enabled": True,
                    "config": {
                        "required_columns": [
                            "created_at",
                            "updated_at",
                        ],
                    },
                },
                {
                    "name": "require_tests",
                    "type": "test",
                    "severity": "warning",
                    "description": "Models should have at least one test",
                    "enabled": True,
                    "config": {
                        "test_coverage_min": 1,
                    },
                },
            ],
            "excluded_models": [
                "stg__tmp_*",
                "int_tmp_*",
            ],
            "included_models": [],
            "datahub": {
                "server": "https://your-datahub-instance.com",
                "token": "your-datahub-access-token",
                "timeout": 30,
            },
        }

    def save(
        self,
        config: GovernanceConfig,
        output_path: Path,
    ) -> None:
        """Save governance configuration to a YAML file.

        Args:
            config: GovernanceConfig to save.
            output_path: Path to save the configuration.
        """
        raw_config = self._serialize_config(config)
        with open(output_path, "w") as f:
            yaml.dump(raw_config, f, default_flow_style=False, indent=2)

    def _serialize_config(self, config: GovernanceConfig) -> Dict[str, Any]:
        """Serialize GovernanceConfig to dictionary.

        Args:
            config: GovernanceConfig to serialize.

        Returns:
            Dictionary representation of the configuration.
        """
        rules = []
        for rule in config.rules:
            rule_dict = {
                "name": rule.name,
                "type": rule.type.value,
                "severity": rule.severity.value,
                "description": rule.description,
                "enabled": rule.enabled,
            }
            rule_dict.update(self._serialize_rule_config(rule.config))
            rules.append(rule_dict)

        result = {"rules": rules}

        if config.excluded_models:
            result["excluded_models"] = config.excluded_models

        if config.included_models:
            result["included_models"] = config.included_models

        if config.datahub:
            result["datahub"] = config.datahub

        return result

    def _serialize_rule_config(self, config: RuleConfig) -> Dict[str, Any]:
        """Serialize RuleConfig to dictionary.

        Args:
            config: RuleConfig to serialize.

        Returns:
            Dictionary representation of the rule config.
        """
        result = {}

        if config.required_ownership_types:
            result["required_ownership_types"] = config.required_ownership_types

        if config.required_tags:
            result["required_tags"] = config.required_tags

        if config.forbidden_tags:
            result["forbidden_tags"] = config.forbidden_tags

        if config.required_description_length > 0:
            result["required_description_length"] = config.required_description_length

        if config.required_columns:
            result["required_columns"] = config.required_columns

        if config.column_descriptions_required:
            result["column_descriptions_required"] = True

        if config.parent_models:
            result["parent_models"] = config.parent_models

        if config.test_coverage_min is not None:
            result["test_coverage_min"] = config.test_coverage_min

        if config.custom_regex:
            result["custom_regex"] = config.custom_regex

        return {"config": result} if result else {}
