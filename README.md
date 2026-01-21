# dbt-datahub-governance

> A CLI tool that enforces data governance by validating dbt models against governance context stored in DataHub. It brings ownership, lineage awareness, and policy enforcement directly into the dbt workflow.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

| Feature | Description |
|---------|-------------|
| **Governance Validation** | Validate dbt models against governance policies defined in DataHub |
| **Ownership Enforcement** | Ensure all models have proper ownership assigned |
| **Lineage Awareness** | Validate model relationships and dependencies |
| **Policy Enforcement** | Check models against organizational data governance policies |
| **Multiple Reporters** | Console, JSON, Markdown, and GitHub comment reporter formats |
| **CI/CD Integration** | Seamlessly integrate into your CI/CD pipelines |

---

## Installation

**1. Clone the repository:**

```bash
git clone https://github.com/karan0207/dbt-datahub-governance.git
cd dbt-datahub-governance
```

**2. Install in development mode:**

```bash
pip install -e ".[dev]"
```

---

## Quick Start

**Step 1:** Configure your DataHub connection in `governance.yml`:

```yaml
datahub:
  server: "http://localhost:8080"
  token: your-gms-token
```

**Step 2:** Create a governance configuration file:

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

**Step 3:** Run governance checks:

```bash
dbt-governance validate --manifest target/manifest.json --config governance.yml
```

---

## Usage

> For a complete list of commands and options, see the [Commands Reference](commands.md).

### Command Line Interface

```bash
dbt-governance [OPTIONS] COMMAND [ARGS]...
```

### Available Commands

| Command | Description |
|---------|-------------|
| `validate` | Validate dbt models against governance rules |
| `report` | Generate governance compliance reports |
| `ingest` | Ingest dbt metadata into DataHub |
| `init` | Generate example governance configuration |

### Options

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to governance configuration file |
| `--datahub-server URL` | DataHub server URL |
| `--datahub-token TOKEN` | DataHub access token |

---

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

---

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

Markdown formatted report for documentation.

---

## Development

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

---

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

---

## License

MIT License 
