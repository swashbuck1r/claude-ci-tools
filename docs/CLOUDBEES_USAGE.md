# Using Claude PR Analysis in CloudBees Workflows

This guide explains how to use the Claude PR Analysis action in CloudBees workflows.

## Quick Start

### 1. Add Required Secrets

In your CloudBees organization, add these secrets:
- `ANTHROPIC_API_KEY`: Your Anthropic API key from https://console.anthropic.com/
- `GITHUB_TOKEN`: GitHub Personal Access Token with `repo` scope

### 2. Create a Workflow

Create `.cloudbees/workflows/pr-analysis.yml` in your repository:

```yaml
apiVersion: automation.cloudbees.io/v1alpha1
kind: workflow
name: PR Analysis

on:
  pull_request:
    types:
      - opened
      - synchronize
      - reopened

jobs:
  analyze:
    steps:
      - name: Analyze PR with Claude
        uses: <your-org>/claude-ci-tools@main
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          pr-number: ${{ cloudbees.scm.pull_request.number }}
          repository: ${{ cloudbees.scm.repository_full_name }}
          post-comment: "true"
```

### 3. Trigger the Workflow

The workflow will automatically run when:
- A new PR is opened
- Commits are pushed to an existing PR
- A closed PR is reopened

## Action Inputs

| Input | Required | Description | Default |
|-------|----------|-------------|---------|
| `anthropic-api-key` | Yes | Anthropic API key for Claude | - |
| `github-token` | Yes | GitHub token for API access | - |
| `pr-number` | Yes | Pull request number to analyze | - |
| `repository` | Yes | Repository in format `owner/repo` | - |
| `post-comment` | No | Post analysis as PR comment | `false` |
| `tools-repository` | No | Repository containing claude-ci-tools | `swashbuck1r/claude-ci-tools` |

## Action Outputs

| Output | Description |
|--------|-------------|
| `analysis-summary` | Summary text from the analysis |
| `quality-score` | Overall quality score (1-10) |

## Usage Examples

### Example 1: Basic PR Analysis

```yaml
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
```

### Example 2: Quality Gate (Fail if Score < 7)

```yaml
jobs:
  analyze:
    steps:
      - name: Analyze PR
        id: analysis
        uses: <your-org>/claude-ci-tools@main
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          pr-number: ${{ cloudbees.scm.pull_request.number }}
          repository: ${{ cloudbees.scm.repository_full_name }}

      - name: Check Quality Gate
        uses: docker://alpine:3.20
        shell: sh
        if: ${{ steps.analysis.outputs.quality-score < 7 }}
        run: |
          echo "⚠️ Quality score below threshold: ${{ steps.analysis.outputs.quality-score }}/10"
          exit 1
```

### Example 3: Post Analysis as PR Comment

```yaml
jobs:
  analyze:
    steps:
      - name: Analyze and Comment
        uses: <your-org>/claude-ci-tools@main
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          pr-number: ${{ cloudbees.scm.pull_request.number }}
          repository: ${{ cloudbees.scm.repository_full_name }}
          post-comment: "true"
```

### Example 4: On-Demand Analysis

```yaml
apiVersion: automation.cloudbees.io/v1alpha1
kind: workflow
name: Manual PR Analysis

on:
  workflow_dispatch:
    inputs:
      pr-number:
        description: "PR number to analyze"
        required: true
        type: number

jobs:
  analyze:
    steps:
      - name: Analyze Specific PR
        uses: <your-org>/claude-ci-tools@main
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          pr-number: ${{ inputs.pr-number }}
          repository: ${{ cloudbees.scm.repository_full_name }}
          post-comment: "true"
```

### Example 5: Multi-Step with Notifications

```yaml
jobs:
  analyze-and-notify:
    steps:
      - name: Analyze PR
        id: analysis
        uses: <your-org>/claude-ci-tools@main
        with:
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          pr-number: ${{ cloudbees.scm.pull_request.number }}
          repository: ${{ cloudbees.scm.repository_full_name }}

      - name: Send Slack Notification
        uses: cloudbees-io/slack-notify@v1
        with:
          message: |
            PR Analysis Complete!
            Repository: ${{ cloudbees.scm.repository_full_name }}
            PR: #${{ cloudbees.scm.pull_request.number }}
            Quality Score: ${{ steps.analysis.outputs.quality-score }}/10
            Summary: ${{ steps.analysis.outputs.analysis-summary }}
          webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## CloudBees Context Variables

These CloudBees-specific variables are available in workflows:

- `${{ cloudbees.scm.pull_request.number }}` - Current PR number
- `${{ cloudbees.scm.repository_full_name }}` - Full repository name (owner/repo)
- `${{ cloudbees.scm.branch }}` - Current branch name
- `${{ cloudbees.scm.sha }}` - Current commit SHA
- `${{ cloudbees.run_id }}` - Workflow run ID
- `${{ cloudbees.workspace }}` - Workflow workspace directory

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"

Make sure the secret is configured in your CloudBees organization:
1. Go to Organization Settings → Secrets
2. Add `ANTHROPIC_API_KEY` with your Anthropic API key

### Error: "GitHub token invalid"

The `GITHUB_TOKEN` needs `repo` scope. Create a new token at:
https://github.com/settings/tokens

### Error: "Could not find PR"

Verify that:
- The PR number is correct
- The repository format is `owner/repo`
- The GitHub token has access to the repository

### Analysis Takes Too Long

Large PRs with many files may take 1-2 minutes. Consider:
- Setting `timeout-minutes: 5` on the step
- Filtering which files to analyze (future enhancement)

## Advanced Configuration

### Using AWS Bedrock Instead

If you want to use AWS Bedrock in CloudBees, modify the action to set:

```yaml
- name: Analyze with Bedrock
  uses: <your-org>/claude-ci-tools@main
  env:
    USE_BEDROCK: "true"
    AWS_REGION: "us-east-1"
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    pr-number: ${{ cloudbees.scm.pull_request.number }}
    repository: ${{ cloudbees.scm.repository_full_name }}
```

Note: You'll need to modify the action's `analyze` step to pass these env vars.

## Output Format

The action produces:

**Console Output:**
```
🤖 Claude PR Analysis

## Summary
[Summary of changes]

## Overall Quality Score: 8/10

## ⚠️ Code Quality Issues
- [Issue 1]
- [Issue 2]

## 🔒 Security Concerns
- [Concern 1]

## ✅ Best Practices Observed
- [Practice 1]

## 💡 Recommendations
- [Recommendation 1]
```

**Structured Outputs:**
- `analysis-summary`: First line of the summary
- `quality-score`: Integer from 1-10

## Best Practices

1. **Always post comments on PRs** - Set `post-comment: "true"` so developers see feedback
2. **Use quality gates** - Fail the build if score is too low
3. **Run on all PR events** - Include `opened`, `synchronize`, and `reopened`
4. **Combine with other checks** - Run alongside tests, linting, and security scans
5. **Monitor API usage** - Anthropic API has rate limits and costs per request

## Example Repository Structure

```
your-repo/
├── .cloudbees/
│   └── workflows/
│       ├── pr-analysis.yml       # Main PR analysis workflow
│       └── manual-analysis.yml   # On-demand analysis
├── src/
├── tests/
└── README.md
```

## Support

For issues or questions:
- Check the main [README](../README.md)
- Review [Bedrock Setup](BEDROCK_SETUP.md) for AWS configuration
- File an issue in the claude-ci-tools repository
