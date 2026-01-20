"""Data models for dbt manifest data."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """dbt node types."""

    MODEL = "model"
    SOURCE = "source"
    SEED = "seed"
    SNAPSHOT = "snapshot"
    TEST = "test"
    ANALYSIS = "analysis"
    MACRO = "macro"
    EXTERNAL = "external"


class MaterializationType(str, Enum):
    """dbt materialization types."""

    TABLE = "table"
    VIEW = "view"
    INCREMENTAL = "incremental"
    EPHEMERAL = "ephemeral"
    SEED = "seed"


class TestType(str, Enum):
    """dbt test types."""

    UNIQUE = "unique"
    NOT_NULL = "not_null"
    ACCEPTED_VALUES = "accepted_values"
    RELATIONSHIPS = "relationships"
    CUSTOM = "custom"


class dbtModel(BaseModel):
    """Represents a dbt model from manifest.json."""

    name: str = Field(..., description="Model name")
    unique_id: str = Field(..., description="Unique identifier in dbt graph")
    resource_type: NodeType = Field(..., description="Type of dbt resource")
    package_name: str = Field(..., description="Name of the dbt package")
    path: str = Field(..., description="Path to model file")
    original_file_path: str = Field(..., description="Original file path")
    description: str = Field(default="", description="Model description")
    columns: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Model columns",
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Model metadata",
    )
    tags: List[str] = Field(default_factory=list, description="Model tags")
    depends_on: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Models this model depends on",
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Model configuration",
    )
    schema_: str = Field(default="", alias="schema", description="Model schema")
    alias: Optional[str] = Field(None, description="Model alias")
    database: Optional[str] = Field(None, description="Model database")
    materialized: Optional[MaterializationType] = Field(
        None,
        description="Materialization type",
    )
    owners: List[str] = Field(default_factory=list, description="Model owners")
    tests: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tests applied to this model",
    )
    compiled: bool = Field(default=False, description="Whether model is compiled")
    patch_path: Optional[str] = Field(None, description="Path to patch")

    class Config:
        populate_by_name = True


class dbtSource(BaseModel):
    """Represents a dbt source from manifest.json."""

    name: str = Field(..., description="Source name")
    source_name: str = Field(..., description="Source definition name")
    database: str = Field(..., description="Source database")
    schema_: str = Field(default="", alias="schema", description="Source schema")
    description: str = Field(default="", description="Source description")
    loader: Optional[str] = Field(None, description="Source loader")
    identifiers: Dict[str, str] = Field(default_factory=dict, description="Identifiers")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Source metadata")
    tags: List[str] = Field(default_factory=list, description="Source tags")
    freshness: Dict[str, Any] = Field(
        default_factory=dict,
        description="Source freshness settings",
    )

    class Config:
        populate_by_name = True


class dbtMacro(BaseModel):
    """Represents a dbt macro from manifest.json."""

    name: str = Field(..., description="Macro name")
    unique_id: str = Field(..., description="Unique macro identifier")
    package_name: str = Field(..., description="Package name")
    path: str = Field(..., description="Macro file path")
    description: str = Field(default="", description="Macro description")
    arguments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Macro arguments",
    )

    class Config:
        populate_by_name = True


class dbtExposure(BaseModel):
    """Represents a dbt exposure from manifest.json."""

    name: str = Field(..., description="Exposure name")
    unique_id: str = Field(..., description="Unique exposure identifier")
    resource_type: NodeType = Field(..., description="Type of exposed resource")
    maturity: Optional[str] = Field(None, description="Maturity level")
    type: str = Field(..., description="Exposure type")
    owner: Dict[str, str] = Field(default_factory=dict, description="Exposure owner")
    description: str = Field(default="", description="Exposure description")
    organization: str = Field(default="", description="Organization name")
    depends_on: List[str] = Field(default_factory=list, description="Dependencies")
    url: Optional[str] = Field(None, description="External URL")


class dbtMetric(BaseModel):
    """Represents a dbt metric from manifest.json."""

    name: str = Field(..., description="Metric name")
    unique_id: str = Field(..., description="Unique metric identifier")
    description: str = Field(default="", description="Metric description")
    label: str = Field(..., description="Metric label")
    type: str = Field(..., description="Metric type")
    sql: Optional[str] = Field(None, description="Metric SQL")
    timestamp: Optional[str] = Field(None, description="Metric timestamp")
    dimensions: List[str] = Field(default_factory=list, description="Metric dimensions")
    filters: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Metric filters",
    )
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metric metadata")


class ManifestMetadata(BaseModel):
    """Metadata about the manifest.json file."""

    dbt_schema_version: str = Field(..., description="dbt schema version")
    dbt_version: str = Field(..., description="dbt version")
    generated_at: datetime = Field(..., description="Generation timestamp")
    invocation_id: str = Field(default="", description="Invocation ID")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment vars")


class ManifestData(BaseModel):
    """Complete parsed manifest data."""

    metadata: ManifestMetadata = Field(..., description="Manifest metadata")
    nodes: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="All nodes in the manifest",
    )
    sources: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="All sources in the manifest",
    )
    exposures: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="All exposures in the manifest",
    )
    metrics: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="All metrics in the manifest",
    )
    macros: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="All macros in the manifest",
    )
    parent_map: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Parent-child relationships",
    )
    child_map: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Child-parent relationships",
    )
    selectors: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Node selectors",
    )
