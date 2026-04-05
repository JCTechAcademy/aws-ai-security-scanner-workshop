"""
Main scanner orchestrator.

Runs all security checks and returns a combined list of findings.
"""
import json
from scanner.iam_checks import check_iam_least_privilege
from scanner.s3_checks import check_s3_security
from scanner.sg_checks import check_security_groups


def run_full_scan():
    """Run every security check and return all findings in one list."""
    findings = []
    print("Running IAM checks...")
    findings.extend(check_iam_least_privilege())
    print("Running S3 checks...")
    findings.extend(check_s3_security())
    print("Running Security Group checks...")
    findings.extend(check_security_groups())
    return findings


def print_summary(findings):
    """Print a quick summary to the terminal."""
    severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for f in findings:
        severity_counts[f.get('severity', 'LOW')] = severity_counts.get(
            f.get('severity', 'LOW'), 0
        ) + 1

    print("\n" + "=" * 60)
    print(f"SCAN COMPLETE — {len(findings)} findings")
    print("=" * 60)
    for severity, count in severity_counts.items():
        print(f"  {severity:10s} {count}")
    print()


if __name__ == '__main__':
    results = run_full_scan()
    print_summary(results)
    print(json.dumps(results, indent=2, default=str))
