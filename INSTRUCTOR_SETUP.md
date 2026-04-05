# Instructor Pre-Class AWS Setup

Everything you need to do in your AWS account before workshop day. Budget ~30 minutes.

## Overview

You will:
1. Create vulnerable resources so the scanner has something to find
2. Create read-only IAM users for students to connect with
3. Verify the scanner runs end-to-end

## Option 1: Automated Setup (Recommended)

Run the helper script:

```bash
cd scripts
chmod +x create_vulnerabilities.sh
./create_vulnerabilities.sh
```

This creates all vulnerable resources and prints their names. Review the script before running — it creates intentionally insecure resources in whatever account your AWS CLI is pointed at.

## Option 2: Manual Setup

### Vulnerable Resources to Create

Aim for 6–8 findings across three severity levels so the dashboard looks meaningful.

**S3 Buckets**
- Bucket 1: `workshop-public-bucket-<random>` with public read ACL and no encryption
- Bucket 2: `workshop-no-block-<random>` with Public Access Block disabled

**IAM Users**
- User 1: `workshop-admin-user` with `AdministratorAccess` policy attached directly
- User 2: `workshop-old-keys-user` with an access key (will show as active, age flagged)

**Security Groups**
- SG 1: `workshop-ssh-open` with inbound rule `0.0.0.0/0:22`
- SG 2: `workshop-rdp-open` with inbound rule `0.0.0.0/0:3389`

### Student Read-Only IAM Users

Create one IAM user per student (or one shared user for everyone):

```bash
aws iam create-user --user-name workshop-student-01
aws iam attach-user-policy \
    --user-name workshop-student-01 \
    --policy-arn arn:aws:iam::aws:policy/SecurityAudit
aws iam create-access-key --user-name workshop-student-01
```

Save the access key ID and secret key to distribute in class. The `SecurityAudit` managed policy gives read-only access across AWS services — students cannot modify anything.

## Verify the Scanner Runs

Before class, confirm everything works end-to-end:

```bash
# Use one of the student access keys you just created
aws configure --profile workshop-test
export AWS_PROFILE=workshop-test

# Add your Anthropic API key to .env
cp .env.example .env
# edit .env

# Run the scanner
python -m scanner.main

# Launch the dashboard
streamlit run dashboard/app.py
```

You should see 6–8 findings and working AI recommendations. If not, debug now — not in front of students.

## Post-Workshop Cleanup

After class, either:
- **Leave everything in place** to re-use for the next cohort, or
- **Delete** the vulnerable resources and student IAM users

To delete student users:
```bash
for user in workshop-student-01 workshop-student-02 ...; do
    aws iam delete-access-key --user-name $user --access-key-id <ID>
    aws iam detach-user-policy --user-name $user \
        --policy-arn arn:aws:iam::aws:policy/SecurityAudit
    aws iam delete-user --user-name $user
done
```

Always rotate the shared Anthropic API key after class.

## Cost Estimate

All resources used here fall under AWS Free Tier. Expected cost: **$0.00** for a typical workshop.
