"""Tests for DataHub client and URN mapper."""

import pytest
from unittest.mock import Mock, patch

from src.datahub.client import DataHubClient
from src.datahub.urn_mapper import URNMapper
from src.models.dbt_models import dbtModel, NodeType, MaterializationType


class TestDataHubClient:
    """Tests for DataHubClient class."""

    def test_init(self):
        """Test client initialization."""
        client = DataHubClient(
            server="https://datahub.example.com",
            token="test-token",
            timeout=60,
        )

        assert client.server == "https://datahub.example.com"
        assert client.token == "test-token"
        assert client.timeout == 60

    def test_server_url_normalization(self):
        """Test that server URL is normalized."""
        client = DataHubClient(
            server="https://datahub.example.com/",
            token="test-token",
        )

        assert client.server == "https://datahub.example.com"

    @patch("requests.get")
    def test_health_check_success(self, mock_get):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = DataHubClient(
            server="https://datahub.example.com",
            token="test-token",
        )

        assert client.health_check() is True

    @patch("requests.get")
    def test_health_check_failure(self, mock_get):
        """Test failed health check."""
        mock_get.side_effect = Exception("Connection failed")

        client = DataHubClient(
            server="https://datahub.example.com",
            token="test-token",
        )

        assert client.health_check() is False

    def test_get_governance_context(self):
        """Test getting governance context."""
        client = DataHubClient(
            server="https://datahub.example.com",
            token="test-token",
        )

        context = client.get_governance_context()

        assert "ownership" in context
        assert "tags" in context
        assert "descriptions" in context
        assert "lineage" in context


class TestURNMapper:
    """Tests for URNMapper class."""

    def test_init(self):
        """Test mapper initialization."""
        mapper = URNMapper(platform="dbt")

        assert mapper.platform == "dbt"
        assert mapper._platform_urn == "urn:li:dataPlatform:dbt"

    def test_model_to_urn(self):
        """Test converting model to URN."""
        model = dbtModel(
            name="stg_orders",
            unique_id="model.my_package.stg_orders",
            resource_type=NodeType.MODEL,
            package_name="my_package",
            path="models/staging/stg_orders.sql",
            original_file_path="models/staging/stg_orders.sql",
            description="",
            columns={},
            meta={},
            tags=[],
            depends_on={"nodes": []},
            config={},
            schema_="analytics",
            database="analytics",
        )

        mapper = URNMapper(platform="dbt")
        urn = mapper.model_to_urn(model)

        assert urn.startswith("urn:li:dataset(")
        assert "stg_orders" in urn
        assert "dbt" in urn

    def test_model_to_urn_with_schema(self):
        """Test converting model with schema to URN."""
        model = dbtModel(
            name="stg_orders",
            unique_id="model.my_package.stg_orders",
            resource_type=NodeType.MODEL,
            package_name="my_package",
            path="models/staging/stg_orders.sql",
            original_file_path="models/staging/stg_orders.sql",
            description="",
            columns={},
            meta={},
            tags=[],
            depends_on={"nodes": []},
            config={},
            schema_="analytics",
            database="analytics",
        )

        mapper = URNMapper(platform="snowflake")
        urn = mapper.model_to_urn(model)

        assert "analytics" in urn
        assert "stg_orders" in urn

    def test_map_manifest(self):
        """Test mapping all models from a manifest."""
        manifest_data = {
            "models": [
                dbtModel(
                    name="stg_orders",
                    unique_id="model.test.stg_orders",
                    resource_type=NodeType.MODEL,
                    package_name="test",
                    path="models/staging/stg_orders.sql",
                    original_file_path="models/staging/stg_orders.sql",
                    description="",
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
            ]
        }

        mapper = URNMapper(platform="dbt")
        entities = mapper.map_manifest(manifest_data)

        assert len(entities) == 2
        assert all("urn:li:dataset" in e["urn"] for e in entities)

    def test_model_to_entity(self):
        """Test converting model to entity."""
        model = dbtModel(
            name="stg_orders",
            unique_id="model.test.stg_orders",
            resource_type=NodeType.MODEL,
            package_name="test",
            path="models/staging/stg_orders.sql",
            original_file_path="models/staging/stg_orders.sql",
            description="Orders staging model",
            columns={
                "order_id": {"type": "int", "description": "Order ID"},
            },
            meta={},
            tags=["staging"],
            depends_on={"nodes": []},
            config={},
            schema_="analytics",
            owners=["data-team@company.com"],
        )

        mapper = URNMapper(platform="dbt")
        entity = mapper.model_to_entity(model)

        assert entity["urn"].startswith("urn:li:dataset")
        assert entity["type"] == "dataset"
        assert "aspects" in entity
        assert "datasetProperties" in entity["aspects"]

    def test_platform_urn_mapping(self):
        """Test platform URN mapping for different platforms."""
        mapper = URNMapper(platform="bigquery")
        assert mapper._platform_urn == "urn:li:dataPlatform:bigquery"

        mapper = URNMapper(platform="snowflake")
        assert mapper._platform_urn == "urn:li:dataPlatform:snowflake"

        mapper = URNMapper(platform="custom")
        assert mapper._platform_urn == "urn:li:dataPlatform:custom"

    def test_urn_to_model_name(self):
        """Test extracting model name from URN."""
        mapper = URNMapper(platform="dbt")

        model_name = mapper.urn_to_model_name(
            "urn:li:dataset(urn:li:dataPlatform:dbt:analytics.stg_orders)"
        )

        assert model_name == "stg_orders"

    def test_urn_to_model_name_invalid(self):
        """Test extracting model name from invalid URN."""
        mapper = URNMapper(platform="dbt")

        model_name = mapper.urn_to_model_name("invalid-urn")

        assert model_name is None
