# Student Guide
## AWS AI Security Scanner Workshop

Welcome! In the next 90 minutes you're going to build a real security tool that scans an AWS account, finds misconfigurations, and uses AI to explain how to fix them.

By the end you'll have a working dashboard running on your laptop that inspects a live AWS account and generates remediation advice from Claude. You'll also have a portfolio project on your GitHub.

**See the finished version live:** https://jcrtech-scanner.streamlit.app
*(Your instructor will share the password)*

---

## Before Workshop Day (Do This At Home — 15 Minutes)

You need to have everything installed and the repo cloned **before** you walk into class. We don't have time during the workshop for installs.

Choose your operating system:

### 🍎 Mac Setup

**1. Install Homebrew** (skip if you already have it)

Open **Terminal** (Cmd+Space, type "Terminal", hit Enter) and paste:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Follow the prompts. This takes about 5 minutes. When it finishes, you may need to run two extra commands it tells you about — copy and paste them.

**2. Install Python, Git, AWS CLI, and VS Code**
```bash
brew install python@3.12 git awscli
brew install --cask visual-studio-code
```

**3. Verify everything installed**
```bash
python3 --version
git --version
aws --version
```
All three should print version numbers. If any error, ask your instructor before workshop day.

**4. Clone the repo**
```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/JCTechAcademy/aws-ai-security-scanner-workshop.git
cd aws-ai-security-scanner-workshop
```

**5. Create a virtual environment and install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll know it worked when your terminal prompt starts with `(venv)`.

**6. Stop here.** You'll get AWS keys and an Anthropic key from your instructor in class.

---

### 🪟 Windows Setup

**1. Open PowerShell as Administrator**

Click Start, type "PowerShell", **right-click** "Windows PowerShell", choose **Run as administrator**.

**2. Install Python, Git, AWS CLI, and VS Code**
```powershell
winget install Python.Python.3.12
winget install Git.Git
winget install Amazon.AWSCLI
winget install Microsoft.VisualStudioCode
```

**3. Close PowerShell completely and reopen it** (this time normal mode, not admin) so the new tools appear on your PATH.

**4. Verify everything installed**
```powershell
python --version
git --version
aws --version
```
All three should print version numbers.

**5. Allow PowerShell to run scripts** (one-time setup, needed for Python virtual environments)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Type `Y` and press Enter when prompted.

**6. Clone the repo**
```powershell
mkdir $HOME\projects -ErrorAction SilentlyContinue
cd $HOME\projects
git clone https://github.com/JCTechAcademy/aws-ai-security-scanner-workshop.git
cd aws-ai-security-scanner-workshop
```

**7. Create a virtual environment and install dependencies**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

You'll know it worked when your terminal prompt starts with `(venv)`.

**8. Stop here.** You'll get AWS keys and an Anthropic key from your instructor in class.

---

## What Will Happen In Class (90 Minutes)

### Minutes 0–10 — The Hook
Your instructor opens with a real security breach story (the 2019 Capital One breach: 100 million records exposed). You'll learn the two principles you're building around:

- **Least Privilege** — give every user and service the *minimum* permissions needed to do its job
- **Zero Trust** — never trust based on location or network, always authenticate and verify

Then you'll see the **finished version** running at https://jcrtech-scanner.streamlit.app so you know exactly where you're headed.

### Minutes 10–15 — Get Your Credentials
Your instructor hands out two things on a slip of paper:

1. **AWS access key ID and secret** — these are read-only credentials for a pre-broken training account
2. **Anthropic API key** for Claude

#### Configure AWS

**Mac Terminal:**
```bash
cd ~/projects/aws-ai-security-scanner-workshop
source venv/bin/activate
aws configure
```

**Windows PowerShell:**
```powershell
cd $HOME\projects\aws-ai-security-scanner-workshop
.\venv\Scripts\Activate.ps1
aws configure
```

When prompted, enter:
- **AWS Access Key ID:** (from instructor)
- **AWS Secret Access Key:** (from instructor)
- **Default region name:** `us-east-1`
- **Default output format:** `json`

Verify it worked:
```bash
aws sts get-caller-identity
```
You should see a JSON response with the AWS account ID and your user ARN.

#### Configure Anthropic

**Mac:**
```bash
cp .env.example .env
nano .env
```

**Windows:**
```powershell
copy .env.example .env
notepad .env
```

You'll see a line that says `ANTHROPIC_API_KEY=sk-ant-your-key-here`. Replace `sk-ant-your-key-here` with the real key your instructor gave you. Save and close.

- **In nano (Mac):** Ctrl+O, Enter, Ctrl+X
- **In notepad (Windows):** File → Save, then close the window

⚠️ **CRITICAL:** Never paste API keys or AWS credentials into a chat, email, screenshot, or screen-share. Treat them like passwords.

### Minutes 15–25 — Tour the Code
Your instructor walks through the scanner modules that are **already written** for you. You don't write these — you read them to understand how `boto3` inspects AWS resources.

Open VS Code:
```bash
code .
```

Look at:
- `scanner/iam_checks.py` — finds risky IAM users and policies
- `scanner/s3_checks.py` — finds public S3 buckets
- `scanner/sg_checks.py` — finds open security groups
- `scanner/main.py` — combines everything

### Minutes 25–35 — Run the Raw Scanner

```bash
python -m scanner.main
```

You should see a JSON dump of 10–15 security findings. Raw, but informative. Your reaction will be: "Useful, but hard to read." That's the perfect setup for what comes next.

### Minutes 35–55 — Build the AI Recommender (You Write This!)

Open `ai/recommender.py` in VS Code. You'll see four TODO comments. Your instructor walks you through each one. The completed file should look something like this:

```python
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Create the Anthropic client
client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

# System prompt — tell Claude how to respond
SYSTEM_PROMPT = """You are a senior AWS cloud security engineer.
For each security finding, explain the risk in plain language,
then give concrete remediation steps grounded in Least Privilege
and Zero Trust principles.

Format your response as:

**RISK:** <one sentence>

**IMPACT:** <what could go wrong>

**FIX:**
1. <step>
2. <step>
3. <step>

Keep under 150 words."""


def get_recommendation(finding: dict) -> str:
    """Send a finding to Claude and get back a recommendation."""
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Finding: {finding}"
        }]
    )
    return message.content[0].text
```

**Test it from the command line:**
```bash
python ai/recommender.py
```
You should see one full Claude-generated recommendation print out. This is the first "wow" moment.

### Minutes 55–75 — Wire Up the Dashboard (You Write This!)

Open `dashboard/app.py`. Fill in the two TODO sections. The completed file looks like:

```python
import streamlit as st
import pandas as pd
from scanner.main import run_full_scan
from ai.recommender import get_recommendation

st.set_page_config(
    page_title="AWS Security Guardian",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ AWS AI Security Scanner")
st.caption("Grounded in Least Privilege & Zero Trust")

if st.button("🔍 Run Full Scan", type="primary"):
    with st.spinner("Scanning AWS account..."):
        findings = run_full_scan()

    if findings:
        df = pd.DataFrame(findings)

        st.subheader("Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔴 Critical", len(df[df['severity'] == 'CRITICAL']))
        c2.metric("🟠 High", len(df[df['severity'] == 'HIGH']))
        c3.metric("🟡 Medium", len(df[df['severity'] == 'MEDIUM']))
        c4.metric("Total", len(df))

        st.subheader("Findings")
        st.dataframe(df, width='stretch')

        st.subheader("🤖 AI Recommendations")
        for finding in findings:
            label = f"[{finding['severity']}] {finding['issue']}"
            with st.expander(label):
                st.markdown(get_recommendation(finding))
    else:
        st.success("No security issues found!")
```

**Launch the dashboard:**
```bash
streamlit run dashboard/app.py
```

Your browser opens at `http://localhost:8501`. Click **🔍 Run Full Scan**, wait 10 seconds, and watch your dashboard come alive with severity metrics, a findings table, and expandable AI recommendation cards.

**This is the wow moment of the workshop.** 🎉

### Minutes 75–85 — Push to GitHub
Save your work as a portfolio project on your own GitHub.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git add ai/recommender.py dashboard/app.py
git commit -m "Complete AI recommender and dashboard"
```

If you don't have a fork yet, create one at github.com (click "Fork" on the workshop repo), then:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/aws-ai-security-scanner-workshop.git
git push
```

### Minutes 85–90 — Wrap & Stretch Goals
Your instructor recaps what you built and shares ideas for extending the project at home.

---

## Troubleshooting Common Errors

These are the actual errors students hit. Find yours, apply the fix.

### `python` command not found (Mac)
Use `python3` instead. Or add this line to your `~/.zshrc`:
```bash
echo 'alias python=python3' >> ~/.zshrc
source ~/.zshrc
```

### `pip install` fails on `boto3` or `cryptography`
Update pip first:
```bash
python -m pip install --upgrade pip
```
Then re-run the install command.

### `aws: command not found` after install
Close your terminal and reopen it so PATH updates pick up the new tools.

### `Unable to locate credentials` when running the scanner
You skipped `aws configure`. Run it again and paste the keys your instructor gave you.

### `KeyError: 'ANTHROPIC_API_KEY'` or AI calls fail
Your `.env` file is missing or still contains the placeholder.
- **Mac:** `cat .env` to check, `nano .env` to fix
- **Windows:** `type .env` to check, `notepad .env` to fix

The line should look like `ANTHROPIC_API_KEY=sk-ant-api03-...` (your real key, not "sk-ant-your-key-here").

### `ModuleNotFoundError: No module named 'scanner'`
You're running Python from the wrong folder. Make sure you're in the project root:
- **Mac:** `cd ~/projects/aws-ai-security-scanner-workshop`
- **Windows:** `cd $HOME\projects\aws-ai-security-scanner-workshop`

Then re-run your command.

### Windows: "running scripts is disabled on this system"
Run this once in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Streamlit browser doesn't open automatically
Look at the terminal where Streamlit is running. Find the line that says `Local URL: http://localhost:8501` and copy/paste it into your browser manually.

### `BadRequestError: credit balance is too low` (Anthropic)
Your Anthropic account is out of credits. Tell your instructor — they may have extras, or you can add $5 of credits at https://console.anthropic.com/settings/billing.

### `(venv)` doesn't appear in my prompt anymore
You closed your terminal. Re-activate the virtual environment:
- **Mac:** `cd ~/projects/aws-ai-security-scanner-workshop && source venv/bin/activate`
- **Windows:** `cd $HOME\projects\aws-ai-security-scanner-workshop ; .\venv\Scripts\Activate.ps1`

### "Address already in use" when running Streamlit
Another Streamlit process is still running. Kill it:
- **Mac:** `pkill -f streamlit`
- **Windows:** Close any other PowerShell windows running Streamlit, or use Task Manager to end Python processes

### `git push` says "permission denied"
You're trying to push to JCTechAcademy directly. You need to **fork** the repo first:
1. Go to https://github.com/JCTechAcademy/aws-ai-security-scanner-workshop
2. Click **Fork** (top right)
3. Then update your local remote:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/aws-ai-security-scanner-workshop.git
```

---

## After the Workshop

Your instructor will rotate the AWS keys after class — they will stop working. To keep using your scanner on your own:

1. Create a free AWS account at https://aws.amazon.com/free
2. Create your own read-only IAM user with the `SecurityAudit` policy
3. Get your own Anthropic API key at https://console.anthropic.com (add $5 of credits — that's enough for hundreds of scans)
4. Run the scanner against your own account

### Stretch Goals to Try at Home

- **Add CloudTrail and GuardDuty checks** — extend the scanner to inspect logging and threat detection
- **Support Azure** — use `azure-sdk-for-python` to scan Azure resources too
- **Schedule automated scans** — use AWS EventBridge to run nightly
- **Export findings to PDF** — generate a "client report" deliverable
- **Add a fix-it button** — let users apply remediations from the dashboard (carefully — needs write permissions)
- **Build a Slack notification integration** — alert a channel when CRITICAL findings appear

---

## Security Reminders

- **Never commit your `.env` file to git.** The `.gitignore` prevents this but always double-check with `git status` before committing.
- **Never share API keys or AWS credentials** in chat, email, screenshots, or screen-shares.
- **The AWS keys your instructor provides are read-only.** You literally cannot break anything in the training account — that's least privilege in action.
- **Treat AWS access keys like passwords.** If you accidentally expose one, rotate it immediately at console.aws.amazon.com → IAM.

---

## Resources

- **Live demo (finished version):** https://jcrtech-scanner.streamlit.app
- **GitHub repo:** https://github.com/JCTechAcademy/aws-ai-security-scanner-workshop
- **AWS docs on least privilege:** https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **AWS Zero Trust whitepaper:** https://aws.amazon.com/security/zero-trust/
- **Anthropic API docs:** https://docs.claude.com
- **Streamlit docs:** https://docs.streamlit.io

---

## Questions?

Ask your instructor during class, or post in the workshop Discord/Slack channel.

See you there! 🛡️
