"""Parser for dbt manifest.json files."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from ..models.dbt_models import (
    dbtModel,
    dbtSource,
    dbtMacro,
    dbtExposure,
    dbtMetric,
    ManifestData,
    ManifestMetadata,
    NodeType,
    MaterializationType,
)


class ManifestParser:
    """Parse dbt manifest.json files."""

    def parse(self, manifest_path: Path) -> Dict[str, Any]:
        """Parse a dbt manifest.json file.

        Args:
            manifest_path: Path to the manifest.json file.

        Returns:
            Dictionary containing parsed models and other data.
        """
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        metadata = self._parse_metadata(manifest.get("metadata", {}))
        models = self._parse_models(manifest.get("nodes", {}))
        sources = self._parse_sources(manifest.get("sources", {}))
        exposures = self._parse_exposures(manifest.get("exposures", {}))
        metrics = self._parse_metrics(manifest.get("metrics", {}))
        macros = self._parse_macros(manifest.get("macros", {}))

        parent_map = manifest.get("parent_map", {})
        child_map = manifest.get("child_map", {})

        return {
            "metadata": metadata,
            "models": models,
            "sources": sources,
            "exposures": exposures,
            "metrics": metrics,
            "macros": macros,
            "parent_map": parent_map,
            "child_map": child_map,
        }

    def _parse_metadata(self, metadata: Dict[str, Any]) -> ManifestMetadata:
        """Parse manifest metadata.

        Args:
            metadata: Raw metadata dictionary.

        Returns:
            ManifestMetadata object.
        """
        from datetime import datetime

        generated_at = metadata.get("generated_at")
        if isinstance(generated_at, str):
            try:
                generated_at = datetime.fromisoformat(
                    generated_at.replace("Z", "+00:00")
                )
            except ValueError:
                from datetime import datetime

                generated_at = datetime.utcnow()

        return ManifestMetadata(
            dbt_schema_version=metadata.get("dbt_schema_version", ""),
            dbt_version=metadata.get("dbt_version", ""),
            generated_at=generated_at or datetime.utcnow(),
            invocation_id=metadata.get("invocation_id", ""),
            env=metadata.get("env", {}),
        )

    def _parse_models(self, nodes: Dict[str, Any]) -> List[dbtModel]:
        """Parse models from nodes.

        Args:
            nodes: Raw nodes dictionary from manifest.

        Returns:
            List of dbtModel objects.
        """
        models = []
        for node_id, node in nodes.items():
            if self._is_model(node):
                model = self._parse_model(node_id, node)
                if model:
                    models.append(model)
        return models

    def _is_model(self, node: Dict[str, Any]) -> bool:
        """Check if a node is a model.

        Args:
            node: Node dictionary.

        Returns:
            True if the node is a model.
        """
        resource_type = node.get("resource_type")
        return resource_type in ("model", "seed")

    def _parse_model(self, node_id: str, node: Dict[str, Any]) -> Optional[dbtModel]:
        """Parse a single model from a node.

        Args:
            node_id: Unique identifier for the node.
            node: Node dictionary.

        Returns:
            dbtModel object or None.
        """
        try:
            resource_type_str = node.get("resource_type", "model")
            try:
                resource_type = NodeType(resource_type_str)
            except ValueError:
                resource_type = NodeType.MODEL

            materialized_str = node.get("config", {}).get("materialized")
            materialized = None
            if materialized_str:
                try:
                    materialized = MaterializationType(materialized_str)
                except ValueError:
                    pass

            schema_val = node.get("schema")
            if not schema_val:
                schema_val = node.get("database")

            model = dbtModel(
                name=node.get("name", node_id),
                unique_id=node_id,
                resource_type=resource_type,
                package_name=self._get_package_name(node_id),
                path=node.get("path", ""),
                original_file_path=node.get("original_file_path", ""),
                description=node.get("description", ""),
                columns=node.get("columns", {}),
                meta=node.get("meta", {}),
                tags=node.get("tags", []),
                depends_on=node.get("depends_on", {}),
                config=node.get("config", {}),
                schema_=schema_val or "",
                alias=node.get("alias"),
                database=node.get("database"),
                materialized=materialized,
                owners=[],
                tests=[],
                compiled=node.get("compiled", False),
                patch_path=node.get("patch_path"),
            )
            return model
        except Exception:
            return None

    def _get_package_name(self, node_id: str) -> str:
        """Extract package name from node ID.

        Args:
            node_id: Node unique identifier.

        Returns:
            Package name.
        """
        parts = node_id.split(".")
        if len(parts) >= 2:
            return parts[1]
        return "root"

    def _parse_sources(self, sources: Dict[str, Any]) -> List[dbtSource]:
        """Parse sources from manifest.

        Args:
            sources: Raw sources dictionary.

        Returns:
            List of dbtSource objects.
        """
        result = []
        for source_id, source in sources.items():
            try:
                schema_val = source.get("schema")
                if not schema_val:
                    schema_val = source.get("database")

                parsed_source = dbtSource(
                    name=source.get("name", source_id),
                    source_name=source.get("source_name", ""),
                    database=source.get("database", ""),
                    schema_=schema_val or "",
                    description=source.get("description", ""),
                    loader=source.get("loader"),
                    identifiers=source.get("identifiers", {}),
                    meta=source.get("meta", {}),
                    tags=source.get("tags", []),
                    freshness=source.get("freshness", {}),
                )
                result.append(parsed_source)
            except Exception:
                continue
        return result

    def _parse_exposures(self, exposures: Dict[str, Any]) -> List[dbtExposure]:
        """Parse exposures from manifest.

        Args:
            exposures: Raw exposures dictionary.

        Returns:
            List of dbtExposure objects.
        """
        result = []
        for exposure_id, exposure in exposures.items():
            try:
                resource_type_str = exposure.get("resource_type", "analysis")
                try:
                    resource_type = NodeType(resource_type_str)
                except ValueError:
                    resource_type = NodeType.ANALYSIS

                parsed_exposure = dbtExposure(
                    name=exposure.get("name", exposure_id),
                    unique_id=exposure_id,
                    resource_type=resource_type,
                    maturity=exposure.get("maturity"),
                    type=exposure.get("type", "dashboard"),
                    owner=exposure.get("owner", {}),
                    description=exposure.get("description", ""),
                    organization=exposure.get("organization", ""),
                    depends_on=exposure.get("depends_on", []),
                    url=exposure.get("url"),
                )
                result.append(parsed_exposure)
            except Exception:
                continue
        return result

    def _parse_metrics(self, metrics: Dict[str, Any]) -> List[dbtMetric]:
        """Parse metrics from manifest.

        Args:
            metrics: Raw metrics dictionary.

        Returns:
            List of dbtMetric objects.
        """
        result = []
        for metric_id, metric in metrics.items():
            try:
                parsed_metric = dbtMetric(
                    name=metric.get("name", metric_id),
                    unique_id=metric_id,
                    description=metric.get("description", ""),
                    label=metric.get("label", metric.get("name", "")),
                    type=metric.get("type", "metric"),
                    sql=metric.get("sql"),
                    timestamp=metric.get("timestamp"),
                    dimensions=metric.get("dimensions", []),
                    filters=metric.get("filters", []),
                    meta=metric.get("meta", {}),
                )
                result.append(parsed_metric)
            except Exception:
                continue
        return result

    def _parse_macros(self, macros: Dict[str, Any]) -> List[dbtMacro]:
        """Parse macros from manifest.

        Args:
            macros: Raw macros dictionary.

        Returns:
            List of dbtMacro objects.
        """
        result = []
        for macro_id, macro in macros.items():
            try:
                parsed_macro = dbtMacro(
                    name=macro.get("name", macro_id),
                    unique_id=macro_id,
                    package_name=self._get_package_name(macro_id),
                    path=macro.get("path", ""),
                    description=macro.get("description", ""),
                    arguments=macro.get("arguments", []),
                )
                result.append(parsed_macro)
            except Exception:
                continue
        return result

    def parse_manifest_data(self, manifest_data: Dict[str, Any]) -> ManifestData:
        """Parse complete manifest into ManifestData object.

        Args:
            manifest_data: Raw manifest dictionary.

        Returns:
            ManifestData object.
        """
        return ManifestData(
            metadata=self._parse_metadata(manifest_data.get("metadata", {})),
            nodes=manifest_data.get("nodes", {}),
            sources=manifest_data.get("sources", {}),
            exposures=manifest_data.get("exposures", {}),
            metrics=manifest_data.get("metrics", {}),
            macros=manifest_data.get("macros", {}),
            parent_map=manifest_data.get("parent_map", {}),
            child_map=manifest_data.get("child_map", {}),
            selectors=manifest_data.get("selectors", {}),
        )
