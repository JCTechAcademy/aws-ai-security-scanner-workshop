# AWS AI Security Scanner Workshop

A 90-minute hands-on workshop where students build an AI-powered security scanner for AWS, grounded in **Least Privilege** and **Zero Trust** principles.

Students connect to a pre-configured AWS account (read-only), run a Python scanner that finds real misconfigurations, and use Claude to generate plain-English remediation guidance displayed on a Streamlit dashboard.

## What Students Will Build

- A Python scanner that inspects IAM, S3, and EC2 security groups via `boto3`
- An AI recommender powered by Claude that turns raw findings into actionable advice
- A Streamlit dashboard showing severity metrics, a findings table, and expandable AI recommendations

## Tech Stack

- Python 3.10+
- `boto3` (AWS SDK)
- `anthropic` (Claude API)
- `streamlit` (dashboard)
- `pandas`

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/JCTechAcademy/aws-ai-security-scanner-workshop.git
cd aws-ai-security-scanner-workshop

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure AWS credentials (instructor provides read-only keys)
aws configure

# 4. Set your Anthropic API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run the scanner from the command line
python -m scanner.main

# 6. Launch the dashboard
streamlit run dashboard/app.py
```

## Repo Structure

```
aws-ai-security-scanner-workshop/
├── README.md                     <- You are here
├── WORKSHOP_GUIDE.md              <- 90-minute instructor playbook
├── INSTRUCTOR_SETUP.md            <- Pre-class AWS setup checklist
├── requirements.txt
├── .env.example
├── .gitignore
├── scripts/
│   └── create_vulnerabilities.sh  <- One-command AWS setup
├── scanner/
│   ├── iam_checks.py              <- Complete
│   ├── s3_checks.py               <- Complete
│   ├── sg_checks.py               <- Complete
│   └── main.py                    <- Complete
├── ai/
│   └── recommender.py             <- Student TODO
├── dashboard/
│   └── app.py                     <- Student TODO
└── solution/                      <- Reference answers
```

## Workshop Files

- **[WORKSHOP_GUIDE.md](WORKSHOP_GUIDE.md)** — the 90-minute agenda for instructors
- **[INSTRUCTOR_SETUP.md](INSTRUCTOR_SETUP.md)** — pre-class AWS account setup

## Security Note

The scanner only requires **read-only** AWS permissions (the `SecurityAudit` managed policy). It cannot modify any resources. This is intentional — the tool practices the same least-privilege principle it teaches.

**Never commit your `.env` file or AWS credentials to GitHub.** The `.gitignore` in this repo prevents this, but always double-check before pushing.

## License

MIT
