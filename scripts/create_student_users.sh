#!/bin/bash
#
# create_student_users.sh
#
# Creates N read-only IAM users for students with the SecurityAudit
# managed policy attached. Outputs their access keys to a CSV you
# can print and hand out in class.
#
# Usage:
#   ./create_student_users.sh 20    # create 20 students

set -e

COUNT=${1:-10}
OUTPUT_FILE="student_credentials.csv"

echo "Creating $COUNT read-only student IAM users..."
echo "username,access_key_id,secret_access_key" > "$OUTPUT_FILE"

for i in $(seq -f "%02g" 1 "$COUNT"); do
    USER="workshop-student-$i"
    echo "  Creating $USER..."

    aws iam create-user --user-name "$USER" > /dev/null 2>&1 || echo "    (exists)"
    aws iam attach-user-policy --user-name "$USER" \
        --policy-arn arn:aws:iam::aws:policy/SecurityAudit

    # Also attach ReadOnlyAccess for broader read visibility
    aws iam attach-user-policy --user-name "$USER" \
        --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

    KEY_JSON=$(aws iam create-access-key --user-name "$USER" 2>/dev/null || echo "")
    if [ -n "$KEY_JSON" ]; then
        ACCESS_KEY=$(echo "$KEY_JSON" | grep AccessKeyId | cut -d'"' -f4)
        SECRET_KEY=$(echo "$KEY_JSON" | grep SecretAccessKey | cut -d'"' -f4)
        echo "$USER,$ACCESS_KEY,$SECRET_KEY" >> "$OUTPUT_FILE"
    fi
done

echo ""
echo "Done. Credentials saved to: $OUTPUT_FILE"
echo "KEEP THIS FILE SECURE — delete after workshop."
echo ""
echo "To delete all student users after the workshop, run:"
echo "  ./delete_student_users.sh $COUNT"
