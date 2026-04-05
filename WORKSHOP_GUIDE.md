# 90-Minute Workshop Guide

Instructor playbook for the AWS AI Security Scanner workshop.

## Before Class

- Complete all steps in [INSTRUCTOR_SETUP.md](INSTRUCTOR_SETUP.md)
- Have student read-only access keys ready to distribute
- Have a shared Anthropic API key (with spending cap) ready, or confirm each student has their own
- Verify the scanner runs end-to-end against your vulnerable account
- Send pre-work to students 3–5 days ahead

## Pre-Work for Students (15 min at home)

1. Install Python 3.10+, VS Code, Git, AWS CLI v2
2. Create a GitHub account
3. Fork this repo
4. Run `pip install -r requirements.txt`
5. Watch the 3-minute pre-work video on IAM, S3, and security groups basics

## The 90-Minute Agenda

### Minutes 0–10 — Hook & Concepts
Open with the 2019 Capital One breach: 100 million records exposed because of an over-permissive IAM role. Ask the room what two principles would have prevented it.

Introduce the pillars in plain language:
- **Least Privilege** — give every user and service the minimum permissions needed
- **Zero Trust** — never trust based on location, always authenticate and verify

Show a slide of the misconfigurations the scanner will catch today.

### Minutes 10–15 — Distribute Credentials & Configure
Hand out read-only AWS access keys. Students run `aws configure` and paste them in. They also copy `.env.example` to `.env` and add the Anthropic API key.

Teachable aside: "The credentials I just gave you only have `SecurityAudit` permissions. You literally cannot break anything in this account. That's least privilege in action."

### Minutes 15–25 — Tour the Starter Repo
Walk through the repo structure in VS Code. Open `scanner/iam_checks.py` and read through it together. Do the same briefly for `s3_checks.py` and `sg_checks.py`. Students see how `boto3` inspects cloud resources.

### Minutes 25–35 — Run the Raw Scanner
```bash
python -m scanner.main
```

Students see a JSON dump of 6–8 findings from your pre-broken account. Reaction is usually "useful but hard to read." Perfect setup for AI.

### Minutes 35–55 — Build the AI Recommender
Students fill in `ai/recommender.py` live with you. This is the heart of the workshop.

Pause for discussion: "Why does the system prompt matter? What happens if we remove 'Least Privilege and Zero Trust' from it?" Have a student try removing it and compare outputs. Teaches prompt engineering as a real skill.

Test from a Python REPL on a single finding to see one full AI recommendation.

### Minutes 55–75 — Wire Up the Dashboard
Students fill in the two TODO sections in `dashboard/app.py`. Run:
```bash
streamlit run dashboard/app.py
```

Browsers light up across the room — severity metrics, findings table, expandable AI recommendations. This is the wow moment.

### Minutes 75–85 — Explore, Discuss, Push to GitHub
Give 5 minutes to click through and read recommendations. Ask students to share the most useful one they found. Then commit and push to their fork.

Critical teaching moment: show `.gitignore` and explain why `.env` must never be committed. Mention that bots scrape GitHub for leaked AWS keys within minutes.

### Minutes 85–90 — Wrap & Next Steps
Recap what they built: a real AI security agent grounded in least privilege and zero trust. Show stretch goals:
- Add CloudTrail and GuardDuty checks
- Support Azure via `azure-sdk-for-python`
- Schedule nightly scans with EventBridge
- Export findings to PDF for a "client report"

Remind them you'll rotate their access keys after class.

## Post-Workshop

- Rotate or delete student IAM users
- Rotate the shared Anthropic API key
- Leave vulnerable resources in place if teaching the workshop again

## Timing Safety Valves

- **Running behind?** Skip the GitHub push and make it homework.
- **Running ahead?** Have students add a 4th check (stale access keys >90 days) from scratch.
- **Single biggest tip:** do a full dry-run of the 90 minutes yourself before teaching.
