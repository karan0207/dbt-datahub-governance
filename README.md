# dbt-datahub-governance

A CLI tool that enforces data governance by validating dbt models against governance context stored in DataHub. It brings ownership, lineage awareness, and policy enforcement directly into the dbt workflow.

## Features

- **Governance Validation**: Validate dbt models against governance policies defined in DataHub
- **Ownership Enforcement**: Ensure all models have proper ownership assigned
- **Lineage Awareness**: Validate model relationships and dependencies
- **Policy Enforcement**: Check models against organizational data governance policies
- **Multiple Reporters**: Console, JSON, Markdown, and GitHub comment reporter formats
- **CI/CD Integration**: Seamlessly integrate into your CI/CD pipelines

## Installation

```bash
pip install dbt-datahub-governance
```

## Quick Start

1. Configure your DataHub connection in `governance.yml`:

```yaml
datahub:
  server: "http://localhost:8080"
  token: your-gms-token
```

2. Create a governance configuration file:

```yaml
rules:
  - name: require_owner
    type: ownership
    severity: error
    config:
      required_ownership_types:
        - "DataOwner"
        - "TechnicalOwner"

  - name: require_description
    type: documentation
    severity: warning
```

3. Run governance checks:

```bash
dbt-governance validate --manifest target/manifest.json --config governance.yml
```

## Usage

### Command Line Interface

```bash
dbt-governance [OPTIONS] COMMAND [ARGS]...
```

### Available Commands

- `validate`: Validate dbt models against governance rules
- `report`: Generate governance compliance reports
- `ingest`: Ingest dbt metadata into DataHub

### Options

- `--manifest PATH`: Path to dbt manifest.json file
- `--config PATH`: Path to governance configuration file
- `--reporter FORMAT`: Output reporter format (console, json, markdown, github)
- `--output PATH`: Output file path (for file-based reporters)

## Configuration

### Governance Configuration

The governance configuration file defines the rules and policies for your dbt models:

```yaml
rules:
  - name: rule_name
    type: ownership|documentation|lineage|column
    severity: error|warning|info
    config:
      # Rule-specific configuration
```

### DataHub Configuration

Configure your DataHub connection:

```yaml
datahub:
  server: "https://your-datahub-instance.com"
  token: your-access-token
  timeout: 30
```

## Reporters

### Console Reporter

Human-readable output in the terminal:

```
✓ Model: stg_orders - All checks passed
✗ Model: stg_customers - Missing ownership (severity: error)
```

### JSON Reporter

Machine-readable JSON output:

```json
{
  "results": [
    {
      "model": "stg_orders",
      "status": "passed",
      "violations": []
    }
  ]
}
```

### Markdown Reporter

Markdown formatted report for documentation:

### GitHub Comment Reporter

Comment format for PRs:

```
## Governance Check Results

| Model | Status | Violations |
|-------|--------|------------|
```

## Development

### Setup

```bash
git clone https://github.com/karan0207/dbt-datahub-governance.git
cd dbt-datahub-governance
pip install -e ".[dev]"
```

### Testing

```bash
pytest tests/
```

### Code Quality

```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
