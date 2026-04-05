"""
S3 security checks.

Inspects S3 buckets for public access, missing encryption, and
misconfigured public access blocks.
"""
import boto3
from botocore.exceptions import ClientError


def check_s3_security():
    """Return a list of S3-related security findings."""
    s3 = boto3.client('s3')
    findings = []

    try:
        buckets = s3.list_buckets().get('Buckets', [])
    except ClientError as e:
        print(f"[S3] Could not list buckets: {e}")
        return findings

    for bucket in buckets:
        name = bucket['Name']

        # --- Check 1: Public access via ACL ---
        try:
            acl = s3.get_bucket_acl(Bucket=name)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                uri = grantee.get('URI', '')
                if 'AllUsers' in uri or 'AuthenticatedUsers' in uri:
                    findings.append({
                        'service': 'S3',
                        'severity': 'CRITICAL',
                        'resource': name,
                        'issue': 'Bucket ACL grants access to "AllUsers" or "AuthenticatedUsers"',
                        'principle_violated': 'Zero Trust',
                        'details': (
                            f"Bucket '{name}' is publicly accessible via ACL. "
                            "Anyone on the internet can read its contents. "
                            "Zero trust requires explicit authentication for every access."
                        ),
                    })
                    break
        except ClientError as e:
            print(f"[S3] Could not read ACL for {name}: {e}")

        # --- Check 2: Public Access Block disabled ---
        try:
            pab = s3.get_public_access_block(Bucket=name)
            config = pab.get('PublicAccessBlockConfiguration', {})
            if not all([
                config.get('BlockPublicAcls'),
                config.get('IgnorePublicAcls'),
                config.get('BlockPublicPolicy'),
                config.get('RestrictPublicBuckets'),
            ]):
                findings.append({
                    'service': 'S3',
                    'severity': 'HIGH',
                    'resource': name,
                    'issue': 'Public Access Block is not fully enabled',
                    'principle_violated': 'Zero Trust',
                    'details': (
                        f"Bucket '{name}' allows public access configurations. "
                        "All four Public Access Block settings should be enabled "
                        "to prevent accidental exposure."
                    ),
                })
        except ClientError as e:
            if 'NoSuchPublicAccessBlockConfiguration' in str(e):
                findings.append({
                    'service': 'S3',
                    'severity': 'HIGH',
                    'resource': name,
                    'issue': 'No Public Access Block configured',
                    'principle_violated': 'Zero Trust',
                    'details': (
                        f"Bucket '{name}' has no Public Access Block at all. "
                        "This is the safety net that prevents accidental public exposure."
                    ),
                })

        # --- Check 3: Encryption at rest ---
        try:
            s3.get_bucket_encryption(Bucket=name)
        except ClientError as e:
            if 'ServerSideEncryptionConfigurationNotFoundError' in str(e):
                findings.append({
                    'service': 'S3',
                    'severity': 'MEDIUM',
                    'resource': name,
                    'issue': 'Bucket does not have default encryption enabled',
                    'principle_violated': 'Zero Trust',
                    'details': (
                        f"Bucket '{name}' stores data unencrypted at rest. "
                        "Enable SSE-S3 or SSE-KMS default encryption."
                    ),
                })

    return findings


if __name__ == '__main__':
    import json
    results = check_s3_security()
    print(json.dumps(results, indent=2, default=str))
