#!/usr/bin/env python3
"""Local testing script for PR analysis."""

import os
import sys
from dotenv import load_dotenv
from .agent import PRAnalysisAgent
from .github_client import GitHubClient
from .types import PRAnalysisContext


def main():
    """Main entry point for local testing."""
    print("🧪 Local PR Analysis Test\n")

    # Load environment variables from .env file
    load_dotenv()

    # Get configuration from .env file
    context = PRAnalysisContext(
        owner=os.getenv("TEST_REPO_OWNER", ""),
        repo=os.getenv("TEST_REPO_NAME", ""),
        pr_number=int(os.getenv("TEST_PR_NUMBER", "0")),
        github_token=os.getenv("GITHUB_TOKEN", ""),
    )

    # Check for Bedrock vs Anthropic API
    use_bedrock = os.getenv("USE_BEDROCK", "").lower() == "true"
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    # Validate configuration
    if use_bedrock:
        print("🔧 Using AWS Bedrock for Claude API")
    else:
        if not anthropic_api_key:
            print("❌ Error: ANTHROPIC_API_KEY not found in .env file (or set USE_BEDROCK=true)", file=sys.stderr)
            sys.exit(1)
        print("🔧 Using Anthropic API")

    if not context.github_token:
        print("❌ Error: GITHUB_TOKEN not found in .env file", file=sys.stderr)
        sys.exit(1)

    if not context.owner or not context.repo:
        print("❌ Error: TEST_REPO_OWNER and TEST_REPO_NAME must be set in .env file", file=sys.stderr)
        sys.exit(1)

    if not context.pr_number or context.pr_number == 0:
        print("❌ Error: TEST_PR_NUMBER must be set in .env file", file=sys.stderr)
        sys.exit(1)

    print(f"📊 Analyzing PR #{context.pr_number} in {context.owner}/{context.repo}...\n")

    try:
        # Fetch PR data
        github_client = GitHubClient(context.github_token)
        pr_data = github_client.get_pr_data(context)

        print("✅ Fetched PR data:")
        print(f"   Title: {pr_data.title}")
        print(f"   Files: {pr_data.changed_files}")
        print(f"   Additions: {pr_data.additions}")
        print(f"   Deletions: {pr_data.deletions}")
        print(f"   Commits: {pr_data.commits}\n")

        # Analyze with Claude
        print("🤖 Running Claude analysis...\n")
        agent = PRAnalysisAgent(
            api_key=anthropic_api_key if not use_bedrock else None,
            use_bedrock=use_bedrock,
            aws_region=aws_region
        )
        analysis = agent.analyze_pr(pr_data)

        # Format and display output
        markdown = agent.format_as_markdown(analysis)
        print(markdown)

        print("\n✨ Analysis complete!")

    except Exception as e:
        print(f"❌ Error during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
