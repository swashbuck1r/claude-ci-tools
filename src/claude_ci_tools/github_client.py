"""GitHub client for fetching PR data."""

from github import Github, Auth
from .types import PRAnalysisContext, PRData, PRFile


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: str):
        """Initialize GitHub client with authentication token."""
        auth = Auth.Token(token)
        self.client = Github(auth=auth)

    def get_pr_data(self, context: PRAnalysisContext) -> PRData:
        """Fetch PR data from GitHub."""
        repo = self.client.get_repo(f"{context.owner}/{context.repo}")
        pr = repo.get_pull(context.pr_number)

        # Fetch PR files
        files = []
        for file in pr.get_files():
            pr_file = PRFile(
                filename=file.filename,
                status=file.status,
                additions=file.additions,
                deletions=file.deletions,
                changes=file.changes,
                patch=file.patch if hasattr(file, "patch") else None,
            )
            files.append(pr_file)

        return PRData(
            title=pr.title,
            body=pr.body,
            files=files,
            commits=pr.commits,
            additions=pr.additions,
            deletions=pr.deletions,
            changed_files=pr.changed_files,
        )

    def post_comment(self, context: PRAnalysisContext, comment: str) -> None:
        """Post a comment on the PR."""
        repo = self.client.get_repo(f"{context.owner}/{context.repo}")
        pr = repo.get_pull(context.pr_number)
        pr.create_issue_comment(comment)
