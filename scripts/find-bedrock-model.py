#!/usr/bin/env python3
"""Helper script to find available Bedrock Claude models."""

import boto3
from anthropic import AnthropicBedrock

# Common Bedrock Claude model IDs to try
MODELS_TO_TRY = [
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-v2:1",
]

def test_model(client, model_id):
    """Test if a model works with a simple prompt."""
    try:
        response = client.messages.create(
            model=model_id,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}],
        )
        return True
    except Exception as e:
        return False

def main():
    print("🔍 Searching for available Claude models in AWS Bedrock...\n")

    # Get AWS session
    session = boto3.Session()
    credentials = session.get_credentials()
    region = session.region_name or "us-east-1"

    print(f"Region: {region}")
    print(f"Account: {credentials.access_key[:10]}...\n")

    # Create Bedrock client
    client = AnthropicBedrock(
        aws_region=region,
        aws_access_key=credentials.access_key,
        aws_secret_key=credentials.secret_key,
        aws_session_token=credentials.token,
    )

    print("Testing model IDs...\n")
    available_models = []

    for model_id in MODELS_TO_TRY:
        print(f"  Testing: {model_id}...", end=" ")
        if test_model(client, model_id):
            print("✅ WORKS!")
            available_models.append(model_id)
        else:
            print("❌ Not available")

    print("\n" + "="*60)
    if available_models:
        print("✅ Available models found:")
        for model in available_models:
            print(f"   • {model}")
        print("\nAdd this to your .env file:")
        print(f"BEDROCK_MODEL_ID={available_models[0]}")
    else:
        print("❌ No Claude models found.")
        print("\nPlease check:")
        print("1. Model access is enabled in AWS Bedrock console")
        print("2. Your IAM role has bedrock:InvokeModel permission")
        print("3. You're using the correct AWS region")

if __name__ == "__main__":
    main()
