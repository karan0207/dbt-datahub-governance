# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-20

### Added

- Initial project setup with CLI entry point
- Configuration loader for governance rules
- dbt manifest parser for parsing manifest.json files
- DataHub client for governance context retrieval
- URN mapper for dbt models to DataHub entities
- Rules engine with built-in governance rules:
  - Ownership rule
  - Documentation rule
  - Tag rule
  - Column rule
  - Lineage rule
  - Test rule
- Reporter system with multiple output formats:
  - Console reporter with rich formatting
  - JSON reporter for machine-readable output
  - Markdown reporter for documentation
  - GitHub comment reporter for PRs
- Comprehensive test suite
- CI/CD workflow for automated testing
- Pre-commit configuration for code quality
- Contributing guidelines

### Features

- Validate dbt models against governance policies
- Support for multiple output formats
- Integration with DataHub for governance context
- Configurable rules with different severity levels
- CI/CD pipeline with linting and testing

### Dependencies

- pydantic for data validation
- pyyaml for configuration parsing
- datahub-rest for DataHub integration
- click for CLI
- rich for console output
- requests for HTTP calls
