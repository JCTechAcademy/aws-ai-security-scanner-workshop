"""
AI Recommender — STUDENT TODO

This file turns a raw security finding into a plain-English
explanation and remediation plan using Claude.

Your job: fill in the TODO sections below.
"""
import os
from dotenv import load_dotenv

# Load the ANTHROPIC_API_KEY from .env
load_dotenv()

# ---------------------------------------------------------------
# TODO #1: Import the Anthropic client
# Hint: from anthropic import Anthropic
# ---------------------------------------------------------------


# ---------------------------------------------------------------
# TODO #2: Create the client using your API key
# Hint: client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
# ---------------------------------------------------------------


# ---------------------------------------------------------------
# TODO #3: Write the system prompt
#
# The system prompt tells Claude who it is and how to respond.
# A good prompt for this tool should:
#   - Say Claude is a senior AWS cloud security engineer
#   - Ask for plain language explanations
#   - Ground advice in Least Privilege and Zero Trust
#   - Specify a format: RISK / IMPACT / FIX
#   - Ask for concise answers (under 150 words)
# ---------------------------------------------------------------
SYSTEM_PROMPT = """YOUR PROMPT HERE"""


def get_recommendation(finding: dict) -> str:
    """
    Send a single finding to Claude and return the AI recommendation.

    Args:
        finding: a dict with keys like severity, resource, issue,
                 principle_violated, details

    Returns:
        A string containing Claude's formatted recommendation.
    """
    # -----------------------------------------------------------
    # TODO #4: Call the Anthropic API
    #
    # Use client.messages.create with these arguments:
    #   model="claude-sonnet-4-5"
    #   max_tokens=400
    #   system=SYSTEM_PROMPT
    #   messages=[{"role": "user", "content": f"Finding: {finding}"}]
    #
    # Then return message.content[0].text
    # -----------------------------------------------------------
    pass


if __name__ == '__main__':
    # Quick test with a fake finding
    test_finding = {
        'service': 'S3',
        'severity': 'CRITICAL',
        'resource': 'my-public-bucket',
        'issue': 'Bucket ACL grants access to AllUsers',
        'principle_violated': 'Zero Trust',
    }
    print(get_recommendation(test_finding))
