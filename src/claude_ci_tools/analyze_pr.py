#!/usr/bin/env python3
"""Main script for analyzing PRs in CI environment."""

import os
import sys
from .agent import PRAnalysisAgent
from .github_client import GitHubClient
from .types import PRAnalysisContext


def main():
    """Main entry point for PR analysis."""
    # Get configuration from environment variables
    repo_full = os.getenv("GITHUB_REPOSITORY", "")
    repo_parts = repo_full.split("/") if repo_full else []

    context = PRAnalysisContext(
        owner=os.getenv("GITHUB_REPOSITORY_OWNER") or (repo_parts[0] if len(repo_parts) > 0 else ""),
        repo=repo_parts[1] if len(repo_parts) > 1 else "",
        pr_number=int(os.getenv("PR_NUMBER", "0")),
        github_token=os.getenv("GITHUB_TOKEN", ""),
    )

    # Check for Bedrock vs Anthropic API
    use_bedrock = os.getenv("USE_BEDROCK", "").lower() == "true"
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    # Validate configuration
    if not use_bedrock and not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required (or set USE_BEDROCK=true)", file=sys.stderr)
        sys.exit(1)

    if not context.github_token:
        print("Error: GITHUB_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not context.owner or not context.repo:
        print("Error: Could not determine repository owner/name from environment", file=sys.stderr)
        sys.exit(1)

    if not context.pr_number or context.pr_number == 0:
        print("Error: PR_NUMBER environment variable is required", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing PR #{context.pr_number} in {context.owner}/{context.repo}...")

    try:
        # Fetch PR data
        github_client = GitHubClient(context.github_token)
        pr_data = github_client.get_pr_data(context)

        print(
            f"Found {pr_data.changed_files} changed files with "
            f"{pr_data.additions} additions and {pr_data.deletions} deletions"
        )

        # Analyze with Claude
        agent = PRAnalysisAgent(
            api_key=anthropic_api_key if not use_bedrock else None,
            use_bedrock=use_bedrock,
            aws_region=aws_region
        )
        analysis = agent.analyze_pr(pr_data)

        # Format output
        markdown = agent.format_as_markdown(analysis)

        # Write to GitHub Actions summary if available
        summary_file = os.getenv("GITHUB_STEP_SUMMARY")
        if summary_file:
            with open(summary_file, "a") as f:
                f.write(markdown)
            print("Analysis written to GitHub Actions summary")

        # Output to console
        print("\n" + markdown)

        # Optional: Post as PR comment
        if os.getenv("POST_COMMENT", "").lower() == "true":
            github_client.post_comment(context, markdown)
            print("Analysis posted as PR comment")

    except Exception as e:
        print(f"Error analyzing PR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
