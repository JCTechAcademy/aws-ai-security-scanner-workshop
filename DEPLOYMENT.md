# Deploying the Scanner to scanner.jcrtechacademy.com

Step-by-step guide to host the AWS AI Security Scanner as a live web app on a subdomain of jcrtechacademy.com.

## Architecture

```
jcrtechacademy.com              (stays wherever it is now, unchanged)
scanner.jcrtechacademy.com  →  CNAME  →  Streamlit Community Cloud
                                         (free, auto-deploys from GitHub)
```

## Part 1 — Add the hosted app to your repo

On your Mac:

```bash
cd ~/projects/aws-ai-security-scanner-workshop

# 1. Copy the hosted dashboard into place
cp ~/Downloads/app_hosted.py dashboard/app_hosted.py

# 2. Create the .streamlit directory and add the example secrets file
mkdir -p .streamlit
cp ~/Downloads/secrets.toml.example .streamlit/secrets.toml.example

# 3. Make sure real secrets never get committed
echo ".streamlit/secrets.toml" >> .gitignore

# 4. Commit and push
git add dashboard/app_hosted.py .streamlit/secrets.toml.example .gitignore
git commit -m "Add hosted dashboard with password gate and credential form"
git push
```

## Part 2 — Deploy to Streamlit Community Cloud (free)

1. Go to **https://share.streamlit.io** and sign in with your GitHub account (the one that owns JCTechAcademy)
2. Click **New app**
3. Fill in the form:
   - **Repository:** `JCTechAcademy/aws-ai-security-scanner-workshop`
   - **Branch:** `main`
   - **Main file path:** `dashboard/app_hosted.py`
   - **App URL (optional):** choose something like `jcrtech-scanner` — this becomes `jcrtech-scanner.streamlit.app`
4. Click **Advanced settings** → **Secrets** and paste:
   ```toml
   app_password = "pick-a-strong-password-here"
   anthropic_api_key = "sk-ant-api03-your-real-key"
   ```
5. Click **Deploy**

In ~2 minutes your app is live at `https://jcrtech-scanner.streamlit.app`. Visit it, enter your password, and verify the credential form loads. (Don't actually scan yet — just confirm the UI works.)

## Part 3 — Point scanner.jcrtechacademy.com at it

### In Squarespace (where your DNS lives):

1. Log in to **Squarespace** → go to your domain **jcrtechacademy.com**
2. Click **DNS Settings** (or **DNS** → **Manage Custom Records**)
3. Add a new **CNAME record**:
   - **Host:** `scanner`
   - **Type:** `CNAME`
   - **Data/Value:** `jcrtech-scanner.streamlit.app` *(or whatever your Streamlit URL is, without the `https://`)*
   - **TTL:** 3600 (or default)
4. Save

### In Streamlit Cloud:

1. Open your app dashboard at share.streamlit.io
2. Click the three-dot menu on your app → **Settings** → **General**
3. Under **Custom subdomain** (or **Custom domain** — label varies), enter `scanner.jcrtechacademy.com`
4. Save

### Wait for DNS propagation

DNS changes take anywhere from 5 minutes to a few hours. Check status:

```bash
dig scanner.jcrtechacademy.com
```

Once it resolves, visit **https://scanner.jcrtechacademy.com** — Streamlit handles HTTPS automatically.

## Part 4 — Test the full flow

1. Visit `https://scanner.jcrtechacademy.com`
2. Enter your shared password
3. The dashboard loads with the credential form
4. Paste a read-only AWS access key and secret key
5. Check the authorization box
6. Click **Run Security Scan**
7. Verify you see findings and AI recommendations

## Part 5 — Share it

Send clients or workshop visitors:
- The URL: `https://scanner.jcrtechacademy.com`
- The shared password (securely — via Signal, not email)
- The "How to create read-only AWS credentials" guide is already built into the app

## Ongoing maintenance

- **Rotating the password:** update it in Streamlit Cloud → app settings → Secrets → Save → app auto-restarts
- **Rotating the Anthropic API key:** same place
- **Deploying code updates:** just `git push` to main — Streamlit Cloud auto-redeploys in ~30 seconds
- **Watching usage:** Streamlit Cloud dashboard shows requests; Anthropic console shows API spend

## Important notes

- **Streamlit Community Cloud is free but public-facing.** The password gate is your only access control. Choose a strong password.
- **Every scan costs Anthropic API credits.** Each finding = 1 Claude call. A scan with 15 findings costs roughly $0.05. Set a spending cap at console.anthropic.com to avoid surprises.
- **Don't commit `.streamlit/secrets.toml`** — it's in `.gitignore`. Secrets live only in Streamlit Cloud's settings panel.
- **Your users' AWS credentials are never logged or stored**, but you're still the one hosting the endpoint. Anyone using the tool is trusting you. Keep the codebase public on GitHub so users can verify what it does.
