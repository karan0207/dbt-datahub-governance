"""Test fixtures and configuration."""

import json
import pytest
from pathlib import Path
from typing import Any, Dict

from src.models.dbt_models import dbtModel, NodeType, MaterializationType
from src.models.governance import (
    GovernanceConfig,
    GovernanceRule,
    RuleConfig,
    RuleType,
    SeverityLevel,
)


@pytest.fixture
def sample_model() -> dbtModel:
    """Create a sample dbt model for testing."""
    return dbtModel(
        name="stg_orders",
        unique_id="model.my_package.stg_orders",
        resource_type=NodeType.MODEL,
        package_name="my_package",
        path="models/staging/stg_orders.sql",
        original_file_path="models/staging/stg_orders.sql",
        description="Staged orders data",
        columns={
            "order_id": {"type": "int", "description": "Unique order identifier"},
            "customer_id": {"type": "int", "description": "Customer reference"},
            "order_date": {"type": "date", "description": "Date of order"},
        },
        meta={"owner": "data-team"},
        tags=["staging", "verified"],
        depends_on={"nodes": ["model.my_package.raw_orders"]},
        config={"materialized": "view"},
        schema_="analytics",
        materialized=MaterializationType.VIEW,
        owners=["data-team@company.com"],
        tests=[{"test_name": "unique"}],
        compiled=True,
    )


@pytest.fixture
def sample_model_no_owner() -> dbtModel:
    """Create a sample dbt model without owners."""
    return dbtModel(
        name="stg_customers",
        unique_id="model.my_package.stg_customers",
        resource_type=NodeType.MODEL,
        package_name="my_package",
        path="models/staging/stg_customers.sql",
        original_file_path="models/staging/stg_customers.sql",
        description="",
        columns={},
        meta={},
        tags=[],
        depends_on={"nodes": []},
        config={},
        schema_="analytics",
    )


@pytest.fixture
def sample_manifest_data() -> Dict[str, Any]:
    """Create sample manifest data for testing."""
    return {
        "metadata": {
            "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v4.json",
            "dbt_version": "1.5.0",
            "generated_at": "2023-06-01T12:00:00Z",
            "invocation_id": "test-invocation-123",
            "env": {},
        },
        "nodes": {
            "model.my_package.stg_orders": {
                "name": "stg_orders",
                "resource_type": "model",
                "package_name": "my_package",
                "path": "models/staging/stg_orders.sql",
                "original_file_path": "models/staging/stg_orders.sql",
                "description": "Staged orders data",
                "columns": {
                    "order_id": {
                        "type": "int",
                        "description": "Unique order identifier",
                    },
                },
                "meta": {},
                "tags": ["staging"],
                "depends_on": {"nodes": ["model.my_package.raw_orders"]},
                "config": {"materialized": "view"},
                "schema": "analytics",
                "database": "analytics",
                "compiled": True,
            },
            "model.my_package.stg_customers": {
                "name": "stg_customers",
                "resource_type": "model",
                "package_name": "my_package",
                "path": "models/staging/stg_customers.sql",
                "original_file_path": "models/staging/stg_customers.sql",
                "description": "",
                "columns": {},
                "meta": {},
                "tags": [],
                "depends_on": {"nodes": []},
                "config": {},
                "schema": "analytics",
                "database": "analytics",
                "compiled": True,
            },
        },
        "sources": {},
        "exposures": {},
        "metrics": {},
        "macros": {},
        "parent_map": {
            "model.my_package.stg_orders": ["model.my_package.raw_orders"],
            "model.my_package.stg_customers": [],
        },
        "child_map": {
            "model.my_package.raw_orders": ["model.my_package.stg_orders"],
        },
        "selectors": {},
    }


@pytest.fixture
def sample_governance_config() -> GovernanceConfig:
    """Create a sample governance configuration."""
    return GovernanceConfig(
        rules=[
            GovernanceRule(
                name="require_owner",
                type=RuleType.OWNERSHIP,
                severity=SeverityLevel.ERROR,
                description="Models must have owners",
                config=RuleConfig(required_ownership_types=["DataOwner"]),
            ),
            GovernanceRule(
                name="require_description",
                type=RuleType.DOCUMENTATION,
                severity=SeverityLevel.WARNING,
                description="Models should have descriptions",
                config=RuleConfig(required_description_length=10),
            ),
        ],
        excluded_models=["stg__tmp_*"],
        included_models=[],
    )


@pytest.fixture
def temp_config_file(tmp_path) -> Path:
    """Create a temporary configuration file."""
    config_content = """
rules:
  - name: require_owner
    type: ownership
    severity: error
    description: Models must have owners
    config:
      required_ownership_types:
        - DataOwner

  - name: require_description
    type: documentation
    severity: warning
    description: Models should have descriptions
    config:
      required_description_length: 10

excluded_models:
  - stg__tmp_*
"""
    config_file = tmp_path / "governance.yml"
    config_file.write_text(config_content)
    return config_file
