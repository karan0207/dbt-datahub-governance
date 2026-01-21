# CLI Commands Reference

Complete reference for all `dbt-governance` CLI commands.

> **Note:** Both `dbt-governance` and `dbt-datahub-governance` commands are available and work identically.

---

## Table of Contents

- [Global Options](#global-options)
- [Commands](#commands)
  - [validate](#validate)
  - [report](#report)
  - [ingest](#ingest)
  - [init](#init)
- [Environment Variables](#environment-variables)
- [Exit Codes](#exit-codes)
- [Reporter Formats](#reporter-formats)
- [Example Workflow](#example-workflow)

---

## Global Options

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `--config PATH` | - | Path to governance configuration file |
| `--datahub-server URL` | `DATAHUB_SERVER` | DataHub server URL |
| `--datahub-token TOKEN` | `DATAHUB_TOKEN` | DataHub access token |
| `--version` | - | Show version information |
| `--help` | - | Show help message |

---

## Commands

### validate

Validate dbt models against governance rules defined in the configuration file.

**Syntax:**

```bash
dbt-governance validate MANIFEST_PATH [OPTIONS]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `MANIFEST_PATH` | Yes | Path to dbt manifest.json file |

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

**Syntax:**

```bash
dbt-governance report MANIFEST_PATH [OPTIONS]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `MANIFEST_PATH` | Yes | Path to dbt manifest.json file |

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

**Syntax:**

```bash
dbt-governance ingest MANIFEST_PATH [OPTIONS]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `MANIFEST_PATH` | Yes | Path to dbt manifest.json file |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--platform NAME` | `dbt` | Data platform for DataHub assets (e.g., `dbt`, `snowflake`, `bigquery`) |

**Prerequisites:**

- DataHub server URL must be set via `--datahub-server` or `DATAHUB_SERVER` environment variable
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

**Syntax:**

```bash
dbt-governance init OUTPUT_PATH [OPTIONS]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `OUTPUT_PATH` | Yes | Path where the configuration file will be created |

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

## Environment Variables

Use environment variables instead of command-line options for sensitive information:

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

---

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success - no violations (or violations below `--fail-on` threshold) |
| `1` | Validation failed - violations met or exceeded `--fail-on` threshold |
| `2` | Configuration or runtime error |

---

## Reporter Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `console` | Human-readable output with colors | Terminal usage, debugging |
| `json` | Machine-readable JSON output | CI/CD pipelines, programmatic processing |
| `markdown` | Markdown formatted report | Documentation, wiki pages |
| `github` | GitHub-flavored Markdown with collapsible sections | Pull request comments |

---

## Example Workflow

A typical governance workflow:

```bash
# 1. Initialize a governance configuration
dbt-governance init governance.yml --example full

# 2. Validate your dbt models
dbt-governance validate target/manifest.json -c governance.yml

# 3. Generate a report for documentation
dbt-governance report target/manifest.json -o governance_report.md

# 4. Ingest metadata into DataHub
dbt-governance ingest target/manifest.json \
  --datahub-server https://datahub.company.com \
  --datahub-token $DATAHUB_TOKEN
```

### CI/CD Integration

```bash
# In your CI pipeline - fail on any error
dbt-governance validate target/manifest.json \
  -c governance.yml \
  -r json \
  -o results.json \
  --fail-on error

# Or be stricter - fail on warnings too
dbt-governance validate target/manifest.json \
  -c governance.yml \
  --fail-on warning
```
