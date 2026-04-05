"""
IAM security checks.

Inspects IAM users, policies, access keys, and account settings for
violations of Least Privilege and Zero Trust principles.
"""
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError


def check_iam_least_privilege():
    """Return a list of IAM-related security findings."""
    iam = boto3.client('iam')
    findings = []

    # --- Check 1: Users with AdministratorAccess attached directly ---
    try:
        users = iam.list_users().get('Users', [])
        for user in users:
            username = user['UserName']
            attached = iam.list_attached_user_policies(UserName=username)
            for policy in attached.get('AttachedPolicies', []):
                if policy['PolicyName'] == 'AdministratorAccess':
                    findings.append({
                        'service': 'IAM',
                        'severity': 'HIGH',
                        'resource': username,
                        'issue': 'User has AdministratorAccess policy attached directly',
                        'principle_violated': 'Least Privilege',
                        'details': (
                            f"User '{username}' has full admin rights. "
                            "Least privilege requires giving users only the specific "
                            "permissions they need for their job."
                        ),
                    })
    except ClientError as e:
        print(f"[IAM] Could not list users: {e}")

    # --- Check 2: Access keys older than 90 days ---
    try:
        users = iam.list_users().get('Users', [])
        now = datetime.now(timezone.utc)
        for user in users:
            username = user['UserName']
            keys = iam.list_access_keys(UserName=username).get('AccessKeyMetadata', [])
            for key in keys:
                if key['Status'] != 'Active':
                    continue
                age_days = (now - key['CreateDate']).days
                if age_days > 90:
                    findings.append({
                        'service': 'IAM',
                        'severity': 'MEDIUM',
                        'resource': f"{username}/{key['AccessKeyId']}",
                        'issue': f'Access key is {age_days} days old and should be rotated',
                        'principle_violated': 'Zero Trust',
                        'details': (
                            "Long-lived credentials violate zero trust. "
                            "Rotate access keys at least every 90 days."
                        ),
                    })
    except ClientError as e:
        print(f"[IAM] Could not list access keys: {e}")

    # --- Check 3: Root account MFA ---
    try:
        summary = iam.get_account_summary().get('SummaryMap', {})
        if summary.get('AccountMFAEnabled', 0) == 0:
            findings.append({
                'service': 'IAM',
                'severity': 'CRITICAL',
                'resource': 'root account',
                'issue': 'Root account does not have MFA enabled',
                'principle_violated': 'Zero Trust',
                'details': (
                    "The root account is the most powerful identity in an AWS "
                    "account. Without MFA, a single compromised password gives "
                    "an attacker complete control."
                ),
            })
    except ClientError as e:
        print(f"[IAM] Could not get account summary: {e}")

    # --- Check 4: Inline policies with wildcard actions ---
    try:
        users = iam.list_users().get('Users', [])
        for user in users:
            username = user['UserName']
            policy_names = iam.list_user_policies(UserName=username).get('PolicyNames', [])
            for policy_name in policy_names:
                policy_doc = iam.get_user_policy(
                    UserName=username, PolicyName=policy_name
                ).get('PolicyDocument', {})
                statements = policy_doc.get('Statement', [])
                if not isinstance(statements, list):
                    statements = [statements]
                for stmt in statements:
                    action = stmt.get('Action', '')
                    if action == '*' or (isinstance(action, list) and '*' in action):
                        findings.append({
                            'service': 'IAM',
                            'severity': 'HIGH',
                            'resource': f"{username}/{policy_name}",
                            'issue': 'Inline policy uses wildcard action "*"',
                            'principle_violated': 'Least Privilege',
                            'details': (
                                "Wildcard actions grant every possible permission. "
                                "List the specific actions the user actually needs."
                            ),
                        })
    except ClientError as e:
        print(f"[IAM] Could not inspect inline policies: {e}")

    return findings


if __name__ == '__main__':
    import json
    results = check_iam_least_privilege()
    print(json.dumps(results, indent=2, default=str))
