#!/bin/bash
#
# create_vulnerabilities.sh
#
# Creates intentionally insecure AWS resources for the workshop.
# Run this ONCE before workshop day in a dedicated training account.
#
# DO NOT run this in a production account.
#
# Safe to re-run: skips resources that already exist.

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
if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "$BUCKET1" --region "$REGION" 2>/dev/null || echo "  (bucket exists or name taken)"
else
    aws s3api create-bucket --bucket "$BUCKET1" --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION" 2>/dev/null || echo "  (bucket exists or name taken)"
fi

# Disable public access block so ACLs actually take effect
aws s3api delete-public-access-block --bucket "$BUCKET1" 2>/dev/null || true

# Flip ownership to allow ACLs (AWS blocks ACLs by default since April 2023)
aws s3api put-bucket-ownership-controls --bucket "$BUCKET1" \
    --ownership-controls 'Rules=[{ObjectOwnership=BucketOwnerPreferred}]' 2>/dev/null || true

# Now the public ACL will actually work
aws s3api put-bucket-acl --bucket "$BUCKET1" --acl public-read 2>/dev/null || \
    echo "  (ACL could not be applied — public access block may still be on)"

# --- S3 Bucket 2: Public Access Block disabled ---
BUCKET2="workshop-no-block-${RANDOM_SUFFIX}"
echo "[2/6] Creating bucket with no public access block: $BUCKET2"
if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "$BUCKET2" --region "$REGION" 2>/dev/null || echo "  (bucket exists or name taken)"
else
    aws s3api create-bucket --bucket "$BUCKET2" --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION" 2>/dev/null || echo "  (bucket exists or name taken)"
fi
aws s3api delete-public-access-block --bucket "$BUCKET2" 2>/dev/null || true

# --- IAM User 1: AdministratorAccess ---
echo "[3/6] Creating IAM user with AdministratorAccess: workshop-admin-user"
aws iam create-user --user-name workshop-admin-user 2>/dev/null || echo "  (already exists)"
aws iam attach-user-policy --user-name workshop-admin-user \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess 2>/dev/null || true

# --- IAM User 2: With access key ---
echo "[4/6] Creating IAM user with access key: workshop-old-keys-user"
aws iam create-user --user-name workshop-old-keys-user 2>/dev/null || echo "  (already exists)"
# Only create a key if user doesn't already have one
EXISTING_KEYS=$(aws iam list-access-keys --user-name workshop-old-keys-user \
    --query 'AccessKeyMetadata[].AccessKeyId' --output text 2>/dev/null || echo "")
if [ -z "$EXISTING_KEYS" ]; then
    aws iam create-access-key --user-name workshop-old-keys-user > /dev/null 2>&1 || true
else
    echo "  (access key already exists)"
fi

# --- Security Group 1: SSH open to world ---
echo "[5/6] Creating security group with SSH open: workshop-ssh-open"
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' --output text)

SG1_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=workshop-ssh-open" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null)

if [ "$SG1_ID" = "None" ] || [ -z "$SG1_ID" ]; then
    SG1_ID=$(aws ec2 create-security-group \
        --group-name workshop-ssh-open \
        --description "Workshop: SSH open to world" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId' --output text)
fi

aws ec2 authorize-security-group-ingress --group-id "$SG1_ID" \
    --protocol tcp --port 22 --cidr 0.0.0.0/0 2>/dev/null || echo "  (rule exists)"

# --- Security Group 2: RDP open to world ---
echo "[6/6] Creating security group with RDP open: workshop-rdp-open"
SG2_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=workshop-rdp-open" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null)

if [ "$SG2_ID" = "None" ] || [ -z "$SG2_ID" ]; then
    SG2_ID=$(aws ec2 create-security-group \
        --group-name workshop-rdp-open \
        --description "Workshop: RDP open to world" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId' --output text)
fi

aws ec2 authorize-security-group-ingress --group-id "$SG2_ID" \
    --protocol tcp --port 3389 --cidr 0.0.0.0/0 2>/dev/null || echo "  (rule exists)"

echo ""
echo "======================================================"
echo "  Setup complete!"
echo "======================================================"
echo "  S3 bucket 1:   $BUCKET1 (public ACL)"
echo "  S3 bucket 2:   $BUCKET2 (no public access block)"
echo "  IAM user 1:    workshop-admin-user (admin access)"
echo "  IAM user 2:    workshop-old-keys-user (active key)"
echo "  Sec group 1:   $SG1_ID (SSH open)"
echo "  Sec group 2:   $SG2_ID (RDP open)"
echo ""
echo "  Next: run the scanner to verify:"
echo "    cd .. && python -m scanner.main"
echo "======================================================"
