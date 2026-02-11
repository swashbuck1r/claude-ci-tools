# AWS Bedrock Setup Guide

This guide explains how to use AWS Bedrock for local development instead of the Anthropic API.

## Prerequisites

1. **AWS Account** with Bedrock access
2. **AWS CLI** configured with credentials
3. **Bedrock Model Access** - Request access to Claude models in your AWS region

## Requesting Model Access

1. Go to AWS Console → Bedrock → Model Access
2. Request access to Claude models (specifically Claude Sonnet)
3. Wait for approval (usually instant)

## AWS Credentials Setup

Ensure your AWS credentials are configured. You can use any of these methods:

### Option 1: AWS CLI Configuration

```bash
aws configure
```

### Option 2: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### Option 3: AWS Profile

```bash
export AWS_PROFILE=your_profile_name
```

## Project Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Find your AWS profile name (especially important for SSO users):

```bash
# List all configured profiles
aws configure list-profiles

# Example output:
# default
# bedrock-claude-infra-bedrock-claude-user
# my-other-profile
```

3. Edit `.env` to enable Bedrock:

```env
# Use AWS Bedrock instead of Anthropic API
USE_BEDROCK=true

# AWS Region for Bedrock
AWS_REGION=us-east-1

# IMPORTANT: AWS Profile name (required for SSO users)
# Use the profile name from step 2
AWS_PROFILE=bedrock-claude-infra-bedrock-claude-user

# GitHub token for PR access
GITHUB_TOKEN=ghp_xxxxx

# Test PR details
TEST_REPO_OWNER=owner
TEST_REPO_NAME=repo
TEST_PR_NUMBER=123
```

4. For SSO users, login before running:

```bash
aws sso login --profile bedrock-claude-infra-bedrock-claude-user
```

3. Install dependencies with Bedrock support:

```bash
pip install -r requirements.txt
```

## Testing

Run the local test script:

```bash
python -m claude_ci_tools.test_local
```

You should see:

```
🧪 Local PR Analysis Test
🔧 Using AWS Bedrock for Claude API
Using AWS Bedrock in region us-east-1 with model us.anthropic.claude-sonnet-4-5-v2:0
...
```

## Available Bedrock Regions

Claude models are available in these AWS regions:

- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `ap-southeast-1` (Singapore)
- `ap-southeast-2` (Sydney)
- `eu-central-1` (Frankfurt)

## Model Mapping

The tool automatically maps model IDs:

| Anthropic API Model      | AWS Bedrock Model                   |
| ------------------------ | ----------------------------------- |
| claude-sonnet-4-20250514 | us.anthropic.claude-sonnet-4-5-v2:0 |

## Troubleshooting

### "AWS credentials not found" Error

**Most common issue for SSO users!**

Solution:

1. Make sure `AWS_PROFILE` is set in your `.env` file
2. Run `aws sso login --profile your-profile-name`
3. Verify with `aws sts get-caller-identity --profile your-profile-name`

### "Access Denied" Error

- Verify model access is granted in AWS Console → Bedrock → Model Access
- Check your AWS credentials have bedrock:InvokeModel permission
- For SSO: Ensure your SSO role has the correct permissions

### "Region Not Supported"

- Verify Claude is available in your AWS region
- Try switching to us-east-1 or us-west-2

### "Could not connect to the endpoint URL"

- Check your AWS region is set correctly
- Verify Bedrock service is available in your region

### SSO Session Expired

If you get credential errors:

```bash
# Refresh your SSO session
aws sso login --profile your-profile-name
```

## CI/CD Setup

For GitHub Actions, you'll want to use the Anthropic API instead:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  # Don't set USE_BEDROCK in CI
```

The tool will automatically use Anthropic API when ANTHROPIC_API_KEY is set and USE_BEDROCK is not true.

## Cost Comparison

AWS Bedrock pricing may differ from Anthropic API pricing. Check current pricing:

- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

## IAM Policy

Minimum IAM policy for Bedrock access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    }
  ]
}
```
