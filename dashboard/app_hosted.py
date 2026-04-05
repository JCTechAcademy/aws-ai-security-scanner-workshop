"""
JCR Tech Academy — AWS AI Security Scanner (Hosted Version)

Public web app that lets any user scan their own AWS account by
providing their credentials at runtime. Credentials are held only
in memory for the duration of a single scan and are never logged
or persisted.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError, NoCredentialsError
from anthropic import Anthropic


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="JCR Tech Academy — AWS Security Scanner",
    page_icon="🛡️",
    layout="wide",
)


# ============================================================
# PASSWORD GATE
# ============================================================
def check_password():
    """Require the shared password before anything else loads."""
    def password_entered():
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🛡️ JCR Tech Academy")
    st.subheader("AWS AI Security Scanner")
    st.markdown("Please enter the access password to continue.")
    st.text_input(
        "Password",
        type="password",
        on_change=password_entered,
        key="password",
    )
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Incorrect password")
    return False


if not check_password():
    st.stop()


# ============================================================
# HEADER
# ============================================================
st.title("🛡️ AWS AI Security Scanner")
st.caption("by JCR Tech Academy — grounded in Least Privilege & Zero Trust")

st.markdown("""
Scan any AWS account for common security misconfigurations and get
plain-English remediation guidance powered by AI.
""")


# ============================================================
# DISCLOSURE & CREDENTIAL GUIDE
# ============================================================
with st.expander("ℹ️ How this works & credential safety", expanded=False):
    st.markdown("""
    **What this tool does:**
    - Uses AWS credentials you provide to run read-only checks against IAM, S3, and EC2
    - Sends each finding to Anthropic's Claude API to generate remediation advice
    - Displays results on this page

    **What this tool does NOT do:**
    - Store, log, or persist your AWS credentials anywhere
    - Make any changes to your AWS account (read-only by design)
    - Share findings with anyone else

    **Your credentials are held in memory for the duration of one scan
    and discarded as soon as the scan completes.**

    Only use credentials for AWS accounts you own or are authorized to audit.
    """)

with st.expander("🔑 How to create read-only AWS credentials (recommended)", expanded=False):
    st.markdown("""
    For your safety, create a dedicated IAM user with read-only permissions
    instead of using admin credentials. Run these commands in your terminal:

    ```bash
    # 1. Create the user
    aws iam create-user --user-name scanner-readonly

    # 2. Attach the SecurityAudit managed policy (read-only)
    aws iam attach-user-policy \\
        --user-name scanner-readonly \\
        --policy-arn arn:aws:iam::aws:policy/SecurityAudit

    # 3. Attach ReadOnlyAccess for broader visibility
    aws iam attach-user-policy \\
        --user-name scanner-readonly \\
        --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

    # 4. Generate access keys
    aws iam create-access-key --user-name scanner-readonly
    ```

    Copy the `AccessKeyId` and `SecretAccessKey` from the output and paste
    them into the form below.

    **When you're done, delete the user** so the keys can never be reused:
    ```bash
    aws iam delete-access-key --user-name scanner-readonly --access-key-id <KEY_ID>
    aws iam detach-user-policy --user-name scanner-readonly --policy-arn arn:aws:iam::aws:policy/SecurityAudit
    aws iam detach-user-policy --user-name scanner-readonly --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
    aws iam delete-user --user-name scanner-readonly
    ```
    """)


# ============================================================
# CREDENTIAL FORM
# ============================================================
st.subheader("Enter AWS Credentials")

col1, col2 = st.columns(2)
with col1:
    access_key = st.text_input("AWS Access Key ID", type="password", placeholder="AKIA...")
with col2:
    secret_key = st.text_input("AWS Secret Access Key", type="password", placeholder="wJal...")

region = st.selectbox(
    "AWS Region",
    ["us-east-1", "us-east-2", "us-west-1", "us-west-2",
     "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1"],
    index=0,
)

authorized = st.checkbox(
    "I confirm I own or have written authorization to audit this AWS account.",
)


# ============================================================
# SCAN LOGIC — all checks run with the session passed in
# ============================================================
def check_iam(session):
    iam = session.client('iam')
    findings = []
    try:
        users = iam.list_users().get('Users', [])
        for user in users:
            policies = iam.list_attached_user_policies(UserName=user['UserName'])
            for p in policies.get('AttachedPolicies', []):
                if p['PolicyName'] == 'AdministratorAccess':
                    findings.append({
                        'service': 'IAM', 'severity': 'HIGH',
                        'resource': user['UserName'],
                        'issue': 'User has AdministratorAccess attached directly',
                        'principle_violated': 'Least Privilege',
                    })
        now = datetime.now(timezone.utc)
        for user in users:
            keys = iam.list_access_keys(UserName=user['UserName']).get('AccessKeyMetadata', [])
            for key in keys:
                if key['Status'] == 'Active' and (now - key['CreateDate']).days > 90:
                    findings.append({
                        'service': 'IAM', 'severity': 'MEDIUM',
                        'resource': f"{user['UserName']}/{key['AccessKeyId']}",
                        'issue': f"Access key is {(now - key['CreateDate']).days} days old",
                        'principle_violated': 'Zero Trust',
                    })
        summary = iam.get_account_summary().get('SummaryMap', {})
        if summary.get('AccountMFAEnabled', 0) == 0:
            findings.append({
                'service': 'IAM', 'severity': 'CRITICAL',
                'resource': 'root account',
                'issue': 'Root account does not have MFA enabled',
                'principle_violated': 'Zero Trust',
            })
    except ClientError as e:
        st.warning(f"IAM check limited: {e.response['Error']['Code']}")
    return findings


def check_s3(session):
    s3 = session.client('s3')
    findings = []
    try:
        buckets = s3.list_buckets().get('Buckets', [])
        for b in buckets:
            name = b['Name']
            try:
                acl = s3.get_bucket_acl(Bucket=name)
                for g in acl.get('Grants', []):
                    uri = g.get('Grantee', {}).get('URI', '')
                    if 'AllUsers' in uri or 'AuthenticatedUsers' in uri:
                        findings.append({
                            'service': 'S3', 'severity': 'CRITICAL',
                            'resource': name,
                            'issue': 'Bucket ACL grants public access',
                            'principle_violated': 'Zero Trust',
                        })
                        break
            except ClientError:
                pass
            try:
                pab = s3.get_public_access_block(Bucket=name)
                cfg = pab.get('PublicAccessBlockConfiguration', {})
                if not all([cfg.get('BlockPublicAcls'), cfg.get('IgnorePublicAcls'),
                            cfg.get('BlockPublicPolicy'), cfg.get('RestrictPublicBuckets')]):
                    findings.append({
                        'service': 'S3', 'severity': 'HIGH',
                        'resource': name,
                        'issue': 'Public Access Block not fully enabled',
                        'principle_violated': 'Zero Trust',
                    })
            except ClientError as e:
                if 'NoSuchPublicAccessBlockConfiguration' in str(e):
                    findings.append({
                        'service': 'S3', 'severity': 'HIGH',
                        'resource': name,
                        'issue': 'No Public Access Block configured',
                        'principle_violated': 'Zero Trust',
                    })
    except ClientError as e:
        st.warning(f"S3 check limited: {e.response['Error']['Code']}")
    return findings


def check_sgs(session):
    ec2 = session.client('ec2')
    findings = []
    sensitive = {22: 'SSH', 3389: 'RDP', 3306: 'MySQL', 5432: 'PostgreSQL', 27017: 'MongoDB'}
    try:
        groups = ec2.describe_security_groups().get('SecurityGroups', [])
        for sg in groups:
            for rule in sg.get('IpPermissions', []):
                for ip in rule.get('IpRanges', []):
                    if ip.get('CidrIp') != '0.0.0.0/0':
                        continue
                    fp, tp = rule.get('FromPort'), rule.get('ToPort')
                    for port, svc in sensitive.items():
                        if fp is not None and tp is not None and fp <= port <= tp:
                            findings.append({
                                'service': 'EC2',
                                'severity': 'CRITICAL' if port in (22, 3389) else 'HIGH',
                                'resource': f"{sg['GroupName']} ({sg['GroupId']})",
                                'issue': f'{svc} port {port} open to 0.0.0.0/0',
                                'principle_violated': 'Least Privilege',
                            })
    except ClientError as e:
        st.warning(f"EC2 check limited: {e.response['Error']['Code']}")
    return findings


# ============================================================
# AI RECOMMENDER
# ============================================================
@st.cache_resource
def get_anthropic_client():
    return Anthropic(api_key=st.secrets["anthropic_api_key"])


SYSTEM_PROMPT = """You are a senior AWS cloud security engineer.
For each finding, explain the risk in plain language, then give
remediation steps grounded in Least Privilege and Zero Trust.

Format:
**RISK:** <one sentence>
**IMPACT:** <what could go wrong>
**FIX:**
1. <step>
2. <step>
3. <step>

Under 150 words."""


def get_recommendation(finding):
    client = get_anthropic_client()
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Finding: {finding}"}]
    )
    return message.content[0].text


# ============================================================
# RUN SCAN BUTTON
# ============================================================
run_disabled = not (access_key and secret_key and authorized)
if st.button("🔍 Run Security Scan", type="primary", disabled=run_disabled):

    # Build an ephemeral session from the form inputs
    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        # Verify credentials before running the full scan
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        st.success(f"✅ Connected to AWS account: {identity['Account']}")
    except (ClientError, NoCredentialsError) as e:
        st.error(f"❌ Could not authenticate to AWS: {e}")
        st.stop()

    with st.spinner("Scanning AWS account..."):
        findings = []
        findings.extend(check_iam(session))
        findings.extend(check_s3(session))
        findings.extend(check_sgs(session))

    # IMPORTANT: explicitly discard the session and credentials
    del session, access_key, secret_key

    if findings:
        df = pd.DataFrame(findings)

        st.subheader("Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔴 Critical", len(df[df['severity'] == 'CRITICAL']))
        c2.metric("🟠 High", len(df[df['severity'] == 'HIGH']))
        c3.metric("🟡 Medium", len(df[df['severity'] == 'MEDIUM']))
        c4.metric("Total", len(df))

        st.subheader("Findings")
        st.dataframe(
            df[['service', 'severity', 'resource', 'issue', 'principle_violated']],
            use_container_width=True,
        )

        st.subheader("🤖 AI Recommendations")
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.get('severity', 'LOW'), 4)
        )
        for finding in sorted_findings:
            label = f"[{finding['severity']}] {finding['issue']} — {finding['resource']}"
            with st.expander(label):
                with st.spinner("Generating AI recommendation..."):
                    st.markdown(get_recommendation(finding))
    else:
        st.success("✅ No security issues found!")

elif run_disabled:
    st.info("Enter your AWS credentials and confirm authorization above to enable the scan button.")


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "© JCR Tech Academy • Credentials are never stored or logged • "
    "Read-only by design • Use only on AWS accounts you are authorized to audit."
)
