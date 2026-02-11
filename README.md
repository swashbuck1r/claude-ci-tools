# Claude CI Tools

Automated PR code review using Claude AI - analyze pull requests for code quality, security issues, and best practices.

## Quick Start (Local Testing)

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd claude-ci-tools
pip install -r requirements.txt
```

### 2. Get API Keys

- **Anthropic API Key**: Get from https://console.anthropic.com/
- **GitHub Token**: Create at https://github.com/settings/tokens (needs `repo` scope)

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` with your settings:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
GITHUB_TOKEN=ghp_xxxxx

TEST_REPO_OWNER=owner
TEST_REPO_NAME=repo
TEST_PR_NUMBER=123
```

### 4. Run Analysis

```bash
python -m claude_ci_tools.test_local
```

You should see Claude analyze the PR and output a detailed code review!

---

## AWS Bedrock Alternative

If you have AWS Bedrock access and want to use it instead of the Anthropic API (e.g., for local development with existing AWS credentials), see the **[Bedrock Setup Guide](docs/BEDROCK_SETUP.md)** for configuration details.

---

## Features

- **PR Analysis**: Automated code review and quality analysis using Claude Sonnet 4
- **Flexible Authentication**: Use Anthropic API or AWS Bedrock
- **GitHub Actions Integration**: Drop-in workflow for CI/CD pipelines
- **Comprehensive Feedback**: Code quality, security concerns, best practices, and recommendations

## Prerequisites

- Python 3.11+
- Anthropic API key (or AWS Bedrock access)
- GitHub Personal Access Token

## CI/CD Integration

### CloudBees Workflows

Add to your repository's `.cloudbees/workflows/pr-analysis.yml`:

```yaml
apiVersion: automation.cloudbees.io/v1alpha1
kind: workflow
name: PR Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  analyze:
    steps:
      - name: Analyze PR
        uses: <your-org>/claude-ci-tools@main
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          pr-number: ${{ cloudbees.scm.pull_request.number }}
          repository: ${{ cloudbees.scm.repository_full_name }}
          post-comment: "true"
```

See [CloudBees Usage Guide](docs/CLOUDBEES_USAGE.md) for detailed examples.

### GitHub Actions

Add to your repository's `.github/workflows/pr-analysis.yml`:

```yaml
name: PR Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  analyze:
    uses: <your-org>/claude-ci-tools/.github/workflows/analyze-pr.yml@main
    with:
      pr_number: ${{ github.event.pull_request.number }}
      post_comment: true
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Required Secrets:**
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/
- `GITHUB_TOKEN`: Automatically provided

## Environment Variables Reference

### Local Testing (Anthropic API)
| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `TEST_REPO_OWNER` | Yes | Repository owner |
| `TEST_REPO_NAME` | Yes | Repository name |
| `TEST_PR_NUMBER` | Yes | Pull request number |

### Local Testing (AWS Bedrock)
See [Bedrock Setup Guide](docs/BEDROCK_SETUP.md) for Bedrock-specific variables.

### GitHub Actions
| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key (use secrets) |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions |
| `PR_NUMBER` | PR number (from workflow input) |
| `POST_COMMENT` | Post analysis as comment (optional) |

## Output

The analysis includes:

- **Summary**: Brief overview of the changes
- **Overall Quality Score**: 1-10 rating
- **Code Quality Issues**: Identified problems in code quality
- **Security Concerns**: Potential security vulnerabilities
- **Best Practices**: Positive observations
- **Recommendations**: Suggestions for improvement

### Example Output

```markdown
# 🤖 Claude PR Analysis

## Summary
This PR adds user authentication functionality with JWT tokens and includes
proper error handling throughout the authentication flow.

## Overall Quality Score: 8/10

## ⚠️ Code Quality Issues
- Password validation could be more robust with additional complexity requirements
- Missing input sanitization in the login endpoint for special characters

## 🔒 Security Concerns
- JWT secret should be stored in environment variables, not hardcoded
- Consider adding rate limiting to prevent brute force attacks

## ✅ Best Practices Observed
- Proper error handling with specific error messages
- Clean separation of concerns between routes and authentication logic
- Good use of password hashing with bcrypt

## 💡 Recommendations
- Add rate limiting to authentication endpoints using a library like Flask-Limiter
- Consider implementing refresh token functionality for better security
- Add logging for failed authentication attempts for security monitoring
```

## How It Works

1. **Fetches PR data** - Gets files, diffs, and metadata from GitHub
2. **Sends to Claude** - Analyzes changes using Claude Sonnet 4 via Bedrock or Anthropic API
3. **Structured analysis** - Returns code quality issues, security concerns, best practices, and recommendations
4. **Outputs results** - Displays in console, GitHub Actions summary, or as PR comments

## Additional Resources

- [Bedrock Setup Guide](docs/BEDROCK_SETUP.md) - Detailed AWS Bedrock configuration
- [GitHub Actions Workflow](.github/workflows/analyze-pr.yml) - Reusable workflow reference
- [Example Workflow](.github/workflows/pr-analysis-example.yml) - Usage example

## License

MIT
