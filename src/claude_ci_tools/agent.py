"""PR Analysis Agent using Claude."""

import os
import re
from typing import Optional
import boto3
from anthropic import Anthropic, AnthropicBedrock
from .types import PRData, AnalysisResult


class PRAnalysisAgent:
    """Agent for analyzing pull requests using Claude."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        use_bedrock: bool = False,
        aws_region: Optional[str] = None
    ):
        """
        Initialize the agent with either Anthropic API or AWS Bedrock.

        Args:
            api_key: Anthropic API key (required if use_bedrock=False)
            model: Model ID to use
            use_bedrock: Whether to use AWS Bedrock instead of Anthropic API
            aws_region: AWS region for Bedrock (defaults to AWS_REGION env var)
        """
        self.use_bedrock = use_bedrock

        if use_bedrock:
            # Use AWS Bedrock with explicit session
            region = aws_region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"

            # Create a boto3 session to get credentials
            # This respects AWS_PROFILE and other credential sources
            profile_name = os.getenv("AWS_PROFILE")
            session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
            credentials = session.get_credentials()

            if not credentials:
                error_msg = "AWS credentials not found. Please:\n"
                error_msg += "  1. Run 'aws sso login' to refresh SSO credentials, OR\n"
                error_msg += "  2. Set AWS_PROFILE in .env file, OR\n"
                error_msg += "  3. Configure AWS credentials with 'aws configure'\n"
                if profile_name:
                    error_msg += f"  (Currently trying to use profile: {profile_name})"
                raise RuntimeError(error_msg)

            # Initialize Bedrock client with explicit credentials
            self.client = AnthropicBedrock(
                aws_region=region,
                aws_access_key=credentials.access_key,
                aws_secret_key=credentials.secret_key,
                aws_session_token=credentials.token,
            )

            # Bedrock uses different model IDs
            # Map Anthropic model IDs to Bedrock model IDs
            bedrock_model_map = {
                "claude-sonnet-4-20250514": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "claude-opus-4-20250514": "us.anthropic.claude-opus-4-20250514-v1:0",
                "claude-3-5-sonnet-20241022": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            }

            # Allow override via environment variable
            self.model = os.getenv("BEDROCK_MODEL_ID") or bedrock_model_map.get(model, model)
            print(f"Using AWS Bedrock in region {region} with model {self.model}")
        else:
            # Use Anthropic API
            if not api_key:
                raise ValueError("api_key is required when not using Bedrock")
            self.client = Anthropic(api_key=api_key)
            self.model = model
            print(f"Using Anthropic API with model {self.model}")

    def analyze_pr(self, pr_data: PRData) -> AnalysisResult:
        """Analyze a pull request and return structured results."""
        prompt = self._build_analysis_prompt(pr_data)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # Extract text from response
        analysis_text = ""
        for block in response.content:
            if block.type == "text":
                analysis_text += block.text

        return self._parse_analysis(analysis_text)

    def _build_analysis_prompt(self, pr_data: PRData) -> str:
        """Build the analysis prompt for Claude."""
        prompt = f"""You are a code review expert analyzing a GitHub pull request. Please provide a thorough analysis of the changes.

PR Title: {pr_data.title}
PR Description: {pr_data.body or 'No description provided'}

Statistics:
- Commits: {pr_data.commits}
- Files Changed: {pr_data.changed_files}
- Additions: {pr_data.additions}
- Deletions: {pr_data.deletions}

Files Changed:
"""

        for file in pr_data.files:
            prompt += f"\n### File: {file.filename} ({file.status})\n"
            prompt += f"+{file.additions} -{file.deletions}\n"

            if file.patch:
                prompt += f"```diff\n{file.patch}\n```\n"

        prompt += """

Please analyze this PR and provide:

1. A brief summary of the changes
2. Code quality issues (if any)
3. Security concerns (if any)
4. Best practices observations
5. Recommendations for improvement
6. An overall quality score from 1-10

Format your response as follows:

SUMMARY:
[Your summary here]

CODE_QUALITY_ISSUES:
- [Issue 1]
- [Issue 2]
(or "None identified" if no issues)

SECURITY_CONCERNS:
- [Concern 1]
- [Concern 2]
(or "None identified" if no concerns)

BEST_PRACTICES:
- [Practice 1]
- [Practice 2]
(or "None identified" if nothing notable)

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
(or "None" if no recommendations)

SCORE: [number from 1-10]
"""

        return prompt

    def _parse_analysis(self, text: str) -> AnalysisResult:
        """Parse Claude's response into structured data."""

        def extract_section(section_name: str) -> list[str]:
            """Extract a section from the analysis text."""
            pattern = rf"{section_name}:\s*([\s\S]*?)(?=\n\n[A-Z_]+:|$)"
            match = re.search(pattern, text, re.IGNORECASE)

            if not match:
                return []

            content = match.group(1).strip()
            if "none identified" in content.lower() or content.lower() == "none":
                return []

            # Extract bullet points
            lines = content.split("\n")
            items = []
            for line in lines:
                line = line.strip()
                if line.startswith("-"):
                    items.append(line[1:].strip())

            return items

        def extract_summary() -> str:
            """Extract the summary section."""
            pattern = r"SUMMARY:\s*([^\n]+(?:\n(?![A-Z_]+:).*)*)"
            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1).strip() if match else "No summary provided"

        def extract_score() -> int:
            """Extract the quality score."""
            pattern = r"SCORE:\s*(\d+)"
            match = re.search(pattern, text, re.IGNORECASE)
            return int(match.group(1)) if match else 7

        return AnalysisResult(
            summary=extract_summary(),
            code_quality_issues=extract_section("CODE_QUALITY_ISSUES"),
            security_concerns=extract_section("SECURITY_CONCERNS"),
            best_practices=extract_section("BEST_PRACTICES"),
            recommendations=extract_section("RECOMMENDATIONS"),
            overall_score=extract_score(),
        )

    def format_as_markdown(self, result: AnalysisResult) -> str:
        """Format analysis result as markdown."""
        markdown = "# 🤖 Claude PR Analysis\n\n"

        markdown += f"## Summary\n{result.summary}\n\n"

        markdown += f"## Overall Quality Score: {result.overall_score}/10\n\n"

        if result.code_quality_issues:
            markdown += "## ⚠️ Code Quality Issues\n"
            for issue in result.code_quality_issues:
                markdown += f"- {issue}\n"
            markdown += "\n"

        if result.security_concerns:
            markdown += "## 🔒 Security Concerns\n"
            for concern in result.security_concerns:
                markdown += f"- {concern}\n"
            markdown += "\n"

        if result.best_practices:
            markdown += "## ✅ Best Practices Observed\n"
            for practice in result.best_practices:
                markdown += f"- {practice}\n"
            markdown += "\n"

        if result.recommendations:
            markdown += "## 💡 Recommendations\n"
            for rec in result.recommendations:
                markdown += f"- {rec}\n"
            markdown += "\n"

        markdown += "\n---\n*Analysis powered by Claude*"

        return markdown
