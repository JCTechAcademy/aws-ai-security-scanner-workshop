"""
EC2 Security Group checks.

Inspects security groups for overly permissive ingress rules that
violate least privilege and zero trust.
"""
import boto3
from botocore.exceptions import ClientError


SENSITIVE_PORTS = {
    22: 'SSH',
    23: 'Telnet',
    3389: 'RDP',
    3306: 'MySQL',
    5432: 'PostgreSQL',
    27017: 'MongoDB',
    6379: 'Redis',
    1433: 'MSSQL',
}


def check_security_groups():
    """Return a list of security group findings."""
    ec2 = boto3.client('ec2')
    findings = []

    try:
        response = ec2.describe_security_groups()
        groups = response.get('SecurityGroups', [])
    except ClientError as e:
        print(f"[EC2] Could not describe security groups: {e}")
        return findings

    for sg in groups:
        sg_id = sg['GroupId']
        sg_name = sg.get('GroupName', 'unknown')

        for rule in sg.get('IpPermissions', []):
            from_port = rule.get('FromPort')
            to_port = rule.get('ToPort')
            protocol = rule.get('IpProtocol', '')

            for ip_range in rule.get('IpRanges', []):
                cidr = ip_range.get('CidrIp', '')
                if cidr != '0.0.0.0/0':
                    continue

                # Rule open to the world — check severity
                if protocol == '-1':
                    findings.append({
                        'service': 'EC2',
                        'severity': 'CRITICAL',
                        'resource': f"{sg_name} ({sg_id})",
                        'issue': 'Security group allows ALL traffic from 0.0.0.0/0',
                        'principle_violated': 'Zero Trust',
                        'details': (
                            "A rule allowing all protocols from anywhere on the "
                            "internet is the worst-case configuration. It trusts "
                            "every source by default."
                        ),
                    })
                    continue

                # Check if sensitive port is exposed
                for port, service_name in SENSITIVE_PORTS.items():
                    if from_port is not None and to_port is not None and \
                       from_port <= port <= to_port:
                        severity = 'CRITICAL' if port in (22, 3389) else 'HIGH'
                        findings.append({
                            'service': 'EC2',
                            'severity': severity,
                            'resource': f"{sg_name} ({sg_id})",
                            'issue': f'{service_name} port {port} open to 0.0.0.0/0',
                            'principle_violated': 'Least Privilege',
                            'details': (
                                f"Security group exposes {service_name} to the entire "
                                "internet. Restrict to specific IP ranges or use a "
                                "bastion host or Session Manager for administrative access."
                            ),
                        })

    return findings


if __name__ == '__main__':
    import json
    results = check_security_groups()
    print(json.dumps(results, indent=2, default=str))
