"""
AI Recommender — REFERENCE SOLUTION

Complete working version of ai/recommender.py for instructors.
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

SYSTEM_PROMPT = """You are a senior AWS cloud security engineer.
For each security finding you receive, explain the risk in plain
language a junior developer can understand, then give concrete
remediation steps grounded in Least Privilege and Zero Trust
principles.

Format your response exactly as:

**RISK:** <one-sentence explanation of the risk>

**IMPACT:** <what could go wrong if this is not fixed>

**FIX:**
1. <first concrete step>
2. <second concrete step>
3. <third concrete step>

Be concise — keep the total response under 150 words. Use AWS CLI
commands or console navigation where helpful."""


def get_recommendation(finding: dict) -> str:
    """Send a finding to Claude and return the AI recommendation."""
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Finding: {finding}"
        }]
    )
    return message.content[0].text


if __name__ == '__main__':
    test_finding = {
        'service': 'S3',
        'severity': 'CRITICAL',
        'resource': 'my-public-bucket',
        'issue': 'Bucket ACL grants access to AllUsers',
        'principle_violated': 'Zero Trust',
    }
    print(get_recommendation(test_finding))
