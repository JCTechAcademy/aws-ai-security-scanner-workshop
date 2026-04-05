#!/bin/bash
#
# delete_student_users.sh
#
# Removes student IAM users created for the workshop.
#
# Usage:
#   ./delete_student_users.sh 20

set -e
COUNT=${1:-10}

echo "Deleting $COUNT student IAM users..."

for i in $(seq -f "%02g" 1 "$COUNT"); do
    USER="workshop-student-$i"
    echo "  Deleting $USER..."

    # Delete all access keys
    KEYS=$(aws iam list-access-keys --user-name "$USER" \
        --query 'AccessKeyMetadata[].AccessKeyId' --output text 2>/dev/null || echo "")
    for KEY in $KEYS; do
        aws iam delete-access-key --user-name "$USER" --access-key-id "$KEY"
    done

    # Detach policies
    aws iam detach-user-policy --user-name "$USER" \
        --policy-arn arn:aws:iam::aws:policy/SecurityAudit 2>/dev/null || true
    aws iam detach-user-policy --user-name "$USER" \
        --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess 2>/dev/null || true

    # Delete user
    aws iam delete-user --user-name "$USER" 2>/dev/null || echo "    (not found)"
done

echo ""
echo "Cleanup complete. Don't forget to also delete student_credentials.csv"
