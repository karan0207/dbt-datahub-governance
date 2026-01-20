"""Data models for governance configuration and violations."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Severity levels for governance violations."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RuleType(str, Enum):
    """Types of governance rules."""

    OWNERSHIP = "ownership"
    DOCUMENTATION = "documentation"
    LINEAGE = "lineage"
    COLUMN = "column"
    TAG = "tag"
    TEST = "test"
    DESCRIPTION = "description"


class OwnershipType(str, Enum):
    """Types of ownership in DataHub."""

    DATAOWNER = "DataOwner"
    TECHNICALOWNER = "TechnicalOwner"
    STEWARD = "Steward"
    DELEGATE = "Delegate"


class RuleConfig(BaseModel):
    """Configuration for a governance rule."""

    required_ownership_types: List[str] = Field(
        default_factory=list,
        description="Required ownership types",
    )
    required_tags: List[str] = Field(
        default_factory=list,
        description="Tags that must be present",
    )
    forbidden_tags: List[str] = Field(
        default_factory=list,
        description="Tags that must not be present",
    )
    required_description_length: int = Field(
        default=0,
        description="Minimum description length",
    )
    required_columns: List[str] = Field(
        default_factory=list,
        description="Columns that must be present",
    )
    column_descriptions_required: bool = Field(
        default=False,
        description="Whether all columns must have descriptions",
    )
    parent_models: List[str] = Field(
        default_factory=list,
        description="Required parent models",
    )
    test_coverage_min: Optional[int] = Field(
        None,
        description="Minimum number of tests per model",
    )
    custom_regex: Optional[str] = Field(
        None,
        description="Custom regex pattern to match",
    )


class GovernanceRule(BaseModel):
    """Definition of a governance rule."""

    name: str = Field(..., description="Rule name")
    type: RuleType = Field(..., description="Type of rule")
    severity: SeverityLevel = Field(
        default=SeverityLevel.WARNING,
        description="Severity of rule violation",
    )
    description: str = Field(default="", description="Rule description")
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    config: RuleConfig = Field(
        default_factory=RuleConfig,
        description="Rule configuration",
    )


class GovernanceConfig(BaseModel):
    """Complete governance configuration."""

    rules: List[GovernanceRule] = Field(
        default_factory=list,
        description="List of governance rules",
    )
    excluded_models: List[str] = Field(
        default_factory=list,
        description="Models excluded from validation",
    )
    included_models: List[str] = Field(
        default_factory=list,
        description="Models included in validation (empty means all)",
    )
    datahub: Optional[Dict[str, Any]] = Field(
        None,
        description="DataHub configuration",
    )


class Violation(BaseModel):
    """Represents a governance violation."""

    rule_name: str = Field(..., description="Name of the violated rule")
    rule_type: RuleType = Field(..., description="Type of the violated rule")
    severity: SeverityLevel = Field(..., description="Severity of the violation")
    model_name: str = Field(..., description="Name of the model with violation")
    model_unique_id: Optional[str] = Field(
        None,
        description="Unique ID of the model",
    )
    message: str = Field(..., description="Violation message")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional violation details",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the violation was detected",
    )


class ValidationResult(BaseModel):
    """Result of a governance validation."""

    total_models: int = Field(..., description="Total models validated")
    passed_models: int = Field(..., description="Models that passed all checks")
    failed_models: int = Field(..., description="Models with violations")
    total_violations: int = Field(..., description="Total violations found")
    error_count: int = Field(..., description="Number of error violations")
    warning_count: int = Field(..., description="Number of warning violations")
    info_count: int = Field(..., description="Number of info violations")
    violations: List[Violation] = Field(
        default_factory=list,
        description="List of all violations",
    )
    duration_seconds: float = Field(
        default=0.0,
        description="Validation duration in seconds",
    )
