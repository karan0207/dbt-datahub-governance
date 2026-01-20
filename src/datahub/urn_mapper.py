"""URN mapper for dbt models to DataHub entities."""

from typing import Any, Dict, List, Optional
from urllib.parse import quote

from ..models.dbt_models import dbtModel


class URNMapper:
    """Maps dbt models to DataHub URNs."""

    PLATFORM_MAP = {
        "dbt": "urn:li:dataPlatform:dbt",
        "bigquery": "urn:li:dataPlatform:bigquery",
        "snowflake": "urn:li:dataPlatform:snowflake",
        "redshift": "urn:li:dataPlatform:redshift",
        "databricks": "urn:li:dataPlatform:databricks",
        "postgres": "urn:li:dataPlatform:postgres",
    }

    def __init__(
        self,
        platform: str = "dbt",
        datahub_client: Optional[Any] = None,
    ):
        """Initialize URN mapper.

        Args:
            platform: Data platform name.
            datahub_client: Optional DataHub client instance.
        """
        self.platform = platform
        self.datahub_client = datahub_client
        self._platform_urn = self.PLATFORM_MAP.get(
            platform,
            f"urn:li:dataPlatform:{platform}",
        )

    def model_to_urn(self, model: dbtModel) -> str:
        """Convert a dbt model to a DataHub URN.

        Args:
            model: dbtModel instance.

        Returns:
            DataHub URN string.
        """
        entity_name = self._get_entity_name(model)
        escaped_name = quote(entity_name, safe="")
        return f"urn:li:dataset({self._platform_urn}:{escaped_name})"

    def _get_entity_name(self, model: dbtModel) -> str:
        """Generate entity name for URN.

        Args:
            model: dbtModel instance.

        Returns:
            Entity name string.
        """
        parts = []

        if model.database:
            parts.append(model.database)

        if model.schema_:
            parts.append(model.schema_)

        parts.append(model.name)

        return ".".join(parts)

    def map_manifest(
        self,
        manifest_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Map all models from a manifest to DataHub entities.

        Args:
            manifest_data: Parsed manifest data.

        Returns:
            List of DataHub entities.
        """
        entities = []
        models = manifest_data.get("models", [])

        for model in models:
            entity = self.model_to_entity(model)
            if entity:
                entities.append(entity)

        return entities

    def model_to_entity(self, model: dbtModel) -> Optional[Dict[str, Any]]:
        """Convert a dbt model to a DataHub entity.

        Args:
            model: dbtModel instance.

        Returns:
            DataHub entity dictionary.
        """
        urn = self.model_to_urn(model)

        entity = {
            "urn": urn,
            "type": "dataset",
            "aspectNames": [
                "datasetProperties",
                "ownership",
                "globalTags",
                "schemaMetadata",
            ],
            "aspects": {},
        }

        dataset_properties = self._create_dataset_properties(model)
        entity["aspects"]["datasetProperties"] = dataset_properties

        ownership = self._create_ownership(model)
        if ownership:
            entity["aspects"]["ownership"] = ownership

        tags = self._create_tags(model)
        if tags:
            entity["aspects"]["globalTags"] = tags

        schema = self._create_schema(model)
        if schema:
            entity["aspects"]["schemaMetadata"] = schema

        return entity

    def _create_dataset_properties(self, model: dbtModel) -> Dict[str, Any]:
        """Create dataset properties aspect.

        Args:
            model: dbtModel instance.

        Returns:
            Dataset properties dictionary.
        """
        return {
            "name": model.name,
            "description": model.description,
            "qualifiedName": self._get_entity_name(model),
            "customProperties": {
                "unique_id": model.unique_id,
                "package_name": model.package_name,
                "path": model.original_file_path,
                "materialized": model.materialized.value
                if model.materialized
                else None,
                "dbt_source": model.resource_type.value,
            },
            "tags": [],
        }

    def _create_ownership(self, model: dbtModel) -> Optional[Dict[str, Any]]:
        """Create ownership aspect.

        Args:
            model: dbtModel instance.

        Returns:
            Ownership dictionary or None.
        """
        if not model.owners:
            return None

        owners = []
        for owner in model.owners:
            owners.append(
                {
                    "owner": f"urn:li:corpuser:{owner}",
                    "type": "DATAOWNER",
                    "source": {},
                }
            )

        return {
            "owners": owners,
            "lastModified": {
                "time": 0,
                "actor": "urn:li:corpuser:system",
            },
        }

    def _create_tags(self, model: dbtModel) -> Optional[Dict[str, Any]]:
        """Create global tags aspect.

        Args:
            model: dbtModel instance.

        Returns:
            Global tags dictionary or None.
        """
        if not model.tags:
            return None

        tags = []
        for tag in model.tags:
            tags.append(
                {
                    "tag": f"urn:li:tag:{tag}",
                }
            )

        return {"tags": tags}

    def _create_schema(self, model: dbtModel) -> Optional[Dict[str, Any]]:
        """Create schema metadata aspect.

        Args:
            model: dbtModel instance.

        Returns:
            Schema metadata dictionary or None.
        """
        if not model.columns:
            return None

        fields = []
        for col_name, col_info in model.columns.items():
            field = {
                "fieldPath": col_name,
                "description": col_info.get("description", ""),
                "type": col_info.get("type", "string"),
                "nativeDataType": col_info.get("type", "string"),
                "nullable": col_info.get("hidden", False) is False,
                "recursive": False,
            }
            fields.append(field)

        return {
            "schemaName": model.name,
            "platform": self._platform_urn,
            "version": 0,
            "hash": "",
            "fields": fields,
            "primaryKeys": [],
            "foreignKeys": [],
        }

    def urn_to_model_name(self, urn: str) -> Optional[str]:
        """Extract model name from a URN.

        Args:
            urn: DataHub URN.

        Returns:
            Model name or None.
        """
        if not urn.startswith("urn:li:dataset("):
            return None

        urn_content = urn[len("urn:li:dataset(") : -1]
        parts = urn_content.split(":")
        if len(parts) >= 2:
            return parts[-1]
        return None
