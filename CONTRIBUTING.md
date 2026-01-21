# Contributing to dbt-datahub-governance

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip or poetry
- Git

### Setting Up Development Environment

1. Fork the repository on GitHub.

2. Clone your fork locally:

```bash
git clone https://github.com/karan0207/dbt-datahub-governance.git
cd dbt-datahub-governance
```

3. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install development dependencies:

```bash
pip install -e ".[dev]"
```

5. Install pre-commit hooks:

```bash
pre-commit install
```

## Development Workflow

### Code Style

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pydocstyle**: Docstring style

Run these checks before committing:

```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
pydocstyle src/
```

### Running Tests

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/). Please use the following format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat(rules): add custom regex rule type

Add support for custom regex pattern matching in governance rules.
This allows users to define flexible validation rules using regular expressions.

Closes #123
```

### Submitting Changes

1. Ensure all tests pass and code quality checks pass.
2. Update documentation if needed.
3. Commit your changes following the commit message format.
4. Push your branch to your fork.
5. Create a pull request against the `main` branch.

## Project Structure

```
dbt-datahub-governance/
├── src/
│   ├── cli.py              # CLI entry point
│   ├── config/
│   │   └── loader.py       # Configuration loader
│   ├── datahub/
│   │   ├── client.py       # DataHub API client
│   │   └── urn_mapper.py   # URN mapping utilities
│   ├── models/
│   │   ├── dbt_models.py   # dbt manifest models
│   │   └── governance.py   # Governance models
│   ├── parsers/
│   │   └── manifest.py     # Manifest parser
│   ├── reporters/
│   │   ├── base.py         # Reporter base class
│   │   ├── console.py      # Console reporter
│   │   ├── github.py       # GitHub comment reporter
│   │   ├── json_reporter.py # JSON reporter
│   │   └── markdown.py     # Markdown reporter
│   └── rules/
│       ├── base.py         # Rule base class
│       ├── builtin.py      # Built-in rules
│       └── engine.py       # Rules engine
├── tests/                   # Test suite
├── examples/               # Example files
├── pyproject.toml         # Project configuration
└── README.md              # Project documentation
```

## Adding New Rules

To add a new governance rule:

1. Create a new rule class in `src/rules/builtin.py` extending `BaseRule`.
2. Register the rule type in `src/models/governance.py` if needed.
3. Add the rule type to `RULE_CLASS_MAP` in `src/rules/engine.py`.
4. Write tests for the new rule.
5. Update documentation.

## Adding New Reporters

To add a new reporter:

1. Create a new reporter class in `src/reporters/` extending `BaseReporter`.
2. Register the reporter in `src/reporters/__init__.py`.
3. Write tests for the new reporter.
4. Update documentation.

## Questions?

If you have questions, please open an issue for discussion.
