#!/bin/bash
#
# create_vulnerabilities.sh
#
# Creates intentionally insecure AWS resources for the workshop.
# Run this ONCE before workshop day in a dedicated training account.
#
# DO NOT run this in a production account.
#
# Usage:
#   chmod +x create_vulnerabilities.sh
#   ./create_vulnerabilities.sh

set -e

RANDOM_SUFFIX=$(date +%s | tail -c 6)
REGION=$(aws configure get region || echo "us-east-1")

echo "======================================================"
echo "  AWS Workshop Vulnerability Setup"
echo "  Region: $REGION"
echo "======================================================"
echo ""
read -p "This creates INSECURE resources. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# --- S3 Bucket 1: Public ACL, no encryption ---
BUCKET1="workshop-public-bucket-${RANDOM_SUFFIX}"
echo ""
echo "[1/6] Creating public S3 bucket: $BUCKET1"
aws s3api create-bucket --bucket "$BUCKET1" --region "$REGION" \
    $([ "$REGION" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=$REGION")
aws s3api delete-public-access-block --bucket "$BUCKET1"
aws s3api put-bucket-acl --bucket "$BUCKET1" --acl public-read

# --- S3 Bucket 2: Public Access Block disabled ---
BUCKET2="workshop-no-block-${RANDOM_SUFFIX}"
echo "[2/6] Creating bucket with no public access block: $BUCKET2"
aws s3api create-bucket --bucket "$BUCKET2" --region "$REGION" \
    $([ "$REGION" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=$REGION")
aws s3api delete-public-access-block --bucket "$BUCKET2"

# --- IAM User 1: AdministratorAccess ---
echo "[3/6] Creating IAM user with AdministratorAccess: workshop-admin-user"
aws iam create-user --user-name workshop-admin-user 2>/dev/null || echo "  (already exists)"
aws iam attach-user-policy --user-name workshop-admin-user \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# --- IAM User 2: With access key (will show as stale after 90 days) ---
echo "[4/6] Creating IAM user with access key: workshop-old-keys-user"
aws iam create-user --user-name workshop-old-keys-user 2>/dev/null || echo "  (already exists)"
aws iam create-access-key --user-name workshop-old-keys-user > /dev/null 2>&1 || echo "  (key already exists)"

# --- Security Group 1: SSH open to world ---
echo "[5/6] Creating security group with SSH open: workshop-ssh-open"
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' --output text)
SG1_ID=$(aws ec2 create-security-group \
    --group-name workshop-ssh-open \
    --description "Workshop: SSH open to world" \
    --vpc-id "$VPC_ID" \
    --query 'GroupId' --output text 2>/dev/null || \
    aws ec2 describe-security-groups --filters "Name=group-name,Values=workshop-ssh-open" \
    --query 'SecurityGroups[0].GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG1_ID" \
    --protocol tcp --port 22 --cidr 0.0.0.0/0 2>/dev/null || echo "  (rule exists)"

# --- Security Group 2: RDP open to world ---
echo "[6/6] Creating security group with RDP open: workshop-rdp-open"
SG2_ID=$(aws ec2 create-security-group \
    --group-name workshop-rdp-open \
    --description "Workshop: RDP open to world" \
    --vpc-id "$VPC_ID" \
    --query 'GroupId' --output text 2>/dev/null || \
    aws ec2 describe-security-groups --filters "Name=group-name,Values=workshop-rdp-open" \
    --query 'SecurityGroups[0].GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG2_ID" \
    --protocol tcp --port 3389 --cidr 0.0.0.0/0 2>/dev/null || echo "  (rule exists)"

echo ""
echo "======================================================"
echo "  Setup complete!"
echo "======================================================"
echo "  S3 bucket 1:   $BUCKET1"
echo "  S3 bucket 2:   $BUCKET2"
echo "  IAM user 1:    workshop-admin-user"
echo "  IAM user 2:    workshop-old-keys-user"
echo "  Sec group 1:   $SG1_ID (ssh open)"
echo "  Sec group 2:   $SG2_ID (rdp open)"
echo ""
echo "  Next: run create_student_users.sh to create read-only"
echo "  IAM users for each student."
echo "======================================================"
