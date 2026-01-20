"""Reporter factory and registry."""

from typing import Dict, Type

from .base import BaseReporter
from .console import ConsoleReporter
from .github import GitHubReporter
from .json_reporter import JSONReporter
from .markdown import MarkdownReporter


_REPORTERS: Dict[str, Type[BaseReporter]] = {
    "console": ConsoleReporter,
    "json": JSONReporter,
    "markdown": MarkdownReporter,
    "github": GitHubReporter,
}


def get_reporter(reporter_type: str) -> BaseReporter:
    """Get a reporter instance by type.

    Args:
        reporter_type: Type of reporter ('console', 'json', 'markdown', 'github').

    Returns:
        BaseReporter instance.

    Raises:
        ValueError: If reporter type is not supported.
    """
    reporter_class = _REPORTERS.get(reporter_type.lower())
    if not reporter_class:
        raise ValueError(
            f"Unsupported reporter type: {reporter_type}. "
            f"Supported types: {list(_REPORTERS.keys())}"
        )
    return reporter_class()


def list_reporters() -> Dict[str, str]:
    """List all available reporters with descriptions.

    Returns:
        Dictionary mapping reporter type to description.
    """
    return {
        "console": "Rich terminal output with colors and tables",
        "json": "Machine-readable JSON format",
        "markdown": "Markdown format for documentation",
        "github": "GitHub-flavored comment format for PRs",
    }


def register_reporter(reporter_type: str, reporter_class: Type[BaseReporter]) -> None:
    """Register a custom reporter.

    Args:
        reporter_type: Unique identifier for the reporter.
        reporter_class: Reporter class to register.
    """
    _REPORTERS[reporter_type] = reporter_class


def unregister_reporter(reporter_type: str) -> bool:
    """Unregister a reporter.

    Args:
        reporter_type: Type of reporter to unregister.

    Returns:
        True if reporter was unregistered, False if not found.
    """
    if reporter_type in _REPORTERS:
        del _REPORTERS[reporter_type]
        return True
    return False
