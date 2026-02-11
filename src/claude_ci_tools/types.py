"""Type definitions for PR analysis."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PRAnalysisContext:
    """Context for PR analysis."""

    owner: str
    repo: str
    pr_number: int
    github_token: str


@dataclass
class PRFile:
    """Information about a file changed in a PR."""

    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


@dataclass
class PRData:
    """Pull request data."""

    title: str
    body: Optional[str]
    files: list[PRFile]
    commits: int
    additions: int
    deletions: int
    changed_files: int


@dataclass
class AnalysisResult:
    """Result of PR analysis."""

    summary: str
    code_quality_issues: list[str]
    security_concerns: list[str]
    best_practices: list[str]
    recommendations: list[str]
    overall_score: int
