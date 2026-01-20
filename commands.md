# CLI Commands

This document describes all available CLI commands for dbt-datahub-governance.

## Global Options

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `--config PATH` | - | Path to governance configuration file |
| `--datahub-server URL` | `DATAHUB_SERVER` | DataHub server URL |
| `--datahub-token TOKEN` | `DATAHUB_TOKEN` | DataHub access token |
| `--version` | - | Show version information |
| `--help` | - | Show help message |

## Commands

### validate

Validate dbt models against governance rules defined in the configuration file.

```bash
dbt-governance validate MANIFEST_PATH [OPTIONS]
```

**Arguments:**
- `MANIFEST_PATH`: Path to dbt manifest.json file (required)

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--config PATH` | `-c` | - | Path to governance configuration file |
| `--reporter FORMAT` | `-r` | `console` | Output format: `console`, `json`, `markdown`, `github` |
| `--output PATH` | `-o` | - | Output file path (for file-based reporters) |
| `--fail-on LEVEL` | - | `error` | Exit with error code on: `error`, `warning`, `never` |

**Examples:**

```bash
# Basic validation with default settings
dbt-governance validate target/manifest.json

# Validate with custom config and JSON output
dbt-governance validate target/manifest.json -c governance.yml -r json -o report.json

# Validate and fail on warnings
dbt-governance validate target/manifest.json --fail-on warning

# Validate with DataHub integration
dbt-governance validate target/manifest.json \
  --config governance.yml \
  --datahub-server https://datahub.company.com \
  --datahub-token $DATAHUB_TOKEN
```

---

### report

Generate a governance compliance report without failing.

```bash
dbt-governance report MANIFEST_PATH [OPTIONS]
```

**Arguments:**
- `MANIFEST_PATH`: Path to dbt manifest.json file (required)

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output PATH` | `-o` | - | Output file path for the report |
| `--format FORMAT` | `-f` | `markdown` | Report format: `json`, `markdown` |

**Examples:**

```bash
# Generate Markdown report
dbt-governance report target/manifest.json -o governance_report.md

# Generate JSON report
dbt-governance report target/manifest.json -f json -o report.json
```

---

### ingest

Ingest dbt model metadata into DataHub.

```bash
dbt-governance ingest MANIFEST_PATH [OPTIONS]
```

**Arguments:**
- `MANIFEST_PATH`: Path to dbt manifest.json file (required)

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--platform NAME` | `dbt` | Data platform for DataHub assets (e.g., `dbt`, `snowflake`, `bigquery`) |

**Prerequisites:**
- DataHub server URL must be set via `--datahub-server` or `DATAHUB_TOKEN` environment variable
- DataHub access token must be set via `--datahub-token` or `DATAHUB_TOKEN` environment variable

**Examples:**

```bash
# Ingest models into DataHub
dbt-governance ingest target/manifest.json \
  --datahub-server https://datahub.company.com \
  --datahub-token $DATAHUB_TOKEN

# Ingest with custom platform
dbt-governance ingest target/manifest.json \
  --platform snowflake \
  --datahub-server https://datahub.company.com \
  --datahub-token $DATAHUB_TOKEN
```

---

### init

Generate an example governance configuration file.

```bash
dbt-governance init OUTPUT_PATH [OPTIONS]
```

**Arguments:**
- `OUTPUT_PATH`: Path where the configuration file will be created (required)

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--example TYPE` | `basic` | Type of example: `basic` or `full` |

**Examples:**

```bash
# Generate basic example
dbt-governance init governance.yml

# Generate full example with all options
dbt-governance init governance.yml --example full
```

---

### help

Show help for any command.

```bash
dbt-governance --help
dbt-governance validate --help
```

## Environment Variables

You can use environment variables instead of command-line options for sensitive information:

| Variable | Description |
|----------|-------------|
| `DATAHUB_SERVER` | DataHub server URL |
| `DATAHUB_TOKEN` | DataHub access token |

**Example:**

```bash
export DATAHUB_SERVER="https://datahub.company.com"
export DATAHUB_TOKEN="your-access-token"

dbt-governance validate target/manifest.json
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success, no violations (or violations below fail-on threshold) |
| 1 | Validation failed (violations met or exceeded fail-on threshold) |
| 1 | Error occurred |

## Reporter Formats

### console (default)
Human-readable output with colors and formatting in the terminal.

### json
Machine-readable JSON output, ideal for CI/CD pipelines and programmatic processing.

### markdown
Markdown formatted report, suitable for documentation and PR comments.

### github
GitHub-flavored Markdown format designed for PR comments with collapsible sections.

## Example Workflow

```bash
# 1. Initialize a governance configuration
dbt-governance init governance.yml --example full

# 2. Validate your dbt models
dbt-governance validate target/manifest.json -c governance.yml -r console

# 3. Generate a report for documentation
dbt-governance report target/manifest.json -c governance.yml -o governance_report.md

# 4. Ingest metadata into DataHub (requires DataHub credentials)
dbt-governance ingest target/manifest.json \
  --datahub-server https://datahub.company.com \
  --datahub-token $DATAHUB_TOKEN
```
