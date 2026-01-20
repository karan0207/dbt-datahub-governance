"""Tests for manifest parser."""

import json
import pytest
from pathlib import Path

from src.parsers.manifest import ManifestParser
from src.models.dbt_models import NodeType


class TestManifestParser:
    """Tests for ManifestParser class."""

    def test_parse_manifest(self, sample_manifest_data, tmp_path):
        """Test parsing a complete manifest."""
        manifest_file = tmp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(sample_manifest_data, f)

        parser = ManifestParser()
        result = parser.parse(manifest_file)

        assert "metadata" in result
        assert "models" in result
        assert len(result["models"]) == 2

    def test_parse_models(self, sample_manifest_data, tmp_path):
        """Test that models are correctly parsed."""
        manifest_file = tmp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(sample_manifest_data, f)

        parser = ManifestParser()
        result = parser.parse(manifest_file)

        model_names = [m.name for m in result["models"]]
        assert "stg_orders" in model_names
        assert "stg_customers" in model_names

    def test_model_properties(self, sample_manifest_data, tmp_path):
        """Test that model properties are correctly parsed."""
        manifest_file = tmp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(sample_manifest_data, f)

        parser = ManifestParser()
        result = parser.parse(manifest_file)

        stg_orders = next(m for m in result["models"] if m.name == "stg_orders")

        assert stg_orders.unique_id == "model.my_package.stg_orders"
        assert stg_orders.resource_type == NodeType.MODEL
        assert stg_orders.package_name == "my_package"
        assert stg_orders.description == "Staged orders data"
        assert stg_orders.schema_ == "analytics"
        assert "order_id" in stg_orders.columns

    def test_empty_manifest(self, tmp_path):
        """Test parsing an empty manifest."""
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text(
            json.dumps(
                {
                    "metadata": {},
                    "nodes": {},
                    "sources": {},
                    "exposures": {},
                    "metrics": {},
                    "macros": {},
                    "parent_map": {},
                    "child_map": {},
                    "selectors": {},
                }
            )
        )

        parser = ManifestParser()
        result = parser.parse(manifest_file)

        assert len(result["models"]) == 0
        assert len(result["sources"]) == 0

    def test_parse_parent_map(self, sample_manifest_data, tmp_path):
        """Test that parent map is included in results."""
        manifest_file = tmp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(sample_manifest_data, f)

        parser = ManifestParser()
        result = parser.parse(manifest_file)

        assert "parent_map" in result
        assert "model.my_package.stg_orders" in result["parent_map"]

    def test_model_with_compile_status(self, sample_manifest_data, tmp_path):
        """Test that compiled status is correctly parsed."""
        manifest_file = tmp_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(sample_manifest_data, f)

        parser = ManifestParser()
        result = parser.parse(manifest_file)

        stg_orders = next(m for m in result["models"] if m.name == "stg_orders")
        assert stg_orders.compiled is True

    def test_parse_invalid_manifest(self, tmp_path):
        """Test parsing an invalid manifest file."""
        manifest_file = tmp_path / "manifest.json"
        manifest_file.write_text("not valid json")

        parser = ManifestParser()

        with pytest.raises(json.JSONDecodeError):
            parser.parse(manifest_file)
