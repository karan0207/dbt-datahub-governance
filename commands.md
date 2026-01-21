# Commands

Reference for the `dbt-governance` CLI. You can also use `dbt-datahub-governance` - both work the same.

## Global Options

```
--config PATH         Path to governance config file
--datahub-server URL  DataHub server URL (or set DATAHUB_SERVER env var)
--datahub-token TOKEN DataHub access token (or set DATAHUB_TOKEN env var)
--version             Show version
--help                Show help
```

## validate

Validates dbt models against your governance rules.

```bash
dbt-governance validate <manifest-path> [options]
```

Options:
- `-c, --config PATH` - Config file path
- `-r, --reporter FORMAT` - Output format: `console` (default), `json`, `markdown`, `github`
- `-o, --output PATH` - Write output to file
- `--fail-on LEVEL` - When to exit with error: `error` (default), `warning`, `never`

Examples:

```bash
# Simple validation
dbt-governance validate target/manifest.json

# With config and JSON output
dbt-governance validate target/manifest.json -c governance.yml -r json -o report.json

# Fail on warnings (stricter)
dbt-governance validate target/manifest.json --fail-on warning

# With DataHub
dbt-governance validate target/manifest.json \
  --config governance.yml \
  --datahub-server https://datahub.company.com \
  --datahub-token $DATAHUB_TOKEN
```

## report

Generates a compliance report (doesn't fail the build).

```bash
dbt-governance report <manifest-path> [options]
```

Options:
- `-o, --output PATH` - Output file
- `-f, --format FORMAT` - `markdown` (default) or `json`

```bash
dbt-governance report target/manifest.json -o governance_report.md
dbt-governance report target/manifest.json -f json -o report.json
```

## ingest

Pushes dbt metadata into DataHub.

```bash
dbt-governance ingest <manifest-path> [options]
```

Options:
- `--platform NAME` - Platform name: `dbt` (default), `snowflake`, `bigquery`, etc.

Requires `DATAHUB_SERVER` and `DATAHUB_TOKEN` to be set (via env vars or flags).

```bash
dbt-governance ingest target/manifest.json \
  --datahub-server https://datahub.company.com \
  --datahub-token $DATAHUB_TOKEN

# With custom platform
dbt-governance ingest target/manifest.json --platform snowflake
```

## init

Creates a starter governance config file.

```bash
dbt-governance init <output-path> [--example basic|full]
```

```bash
dbt-governance init governance.yml
dbt-governance init governance.yml --example full
```

## Exit Codes

- `0` - Success (or violations below your `--fail-on` threshold)
- `1` - Validation failed
- `2` - Config or runtime error

## Reporter Formats

- `console` - Pretty terminal output with colors
- `json` - For CI/CD and scripts
- `markdown` - For docs
- `github` - For PR comments (collapsible sections)

## Typical Workflow

```bash
# Create a config
dbt-governance init governance.yml

# Run validation
dbt-governance validate target/manifest.json -c governance.yml

# Generate a report
dbt-governance report target/manifest.json -o report.md

# Push to DataHub
dbt-governance ingest target/manifest.json
```

For CI, you probably want:

```bash
dbt-governance validate target/manifest.json -c governance.yml -r json -o results.json --fail-on error
```
