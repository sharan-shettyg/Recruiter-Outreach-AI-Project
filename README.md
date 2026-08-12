# Recruiter Outreach Assistant — Version 0

A simple local MVP:

1. Upload resume PDF
2. Paste job description
3. Enter recruiter name + email
4. Claude generates personalized outreach
5. Review/edit
6. Create a Gmail draft
7. Send manually from Gmail

## 1. Create virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure Claude

Copy `.env.example` to `.env`.

Add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_key_here
CLAUDE_MODEL=claude-sonnet-5
```

## 3. Run the app

```bash
streamlit run app.py
```

At this point, Claude email generation should work.

## 4. Configure Gmail draft access

In Google Cloud:

1. Create/select a Google Cloud project.
2. Enable the Gmail API.
3. Configure Google Auth / OAuth consent.
4. Create an OAuth 2.0 Client ID with application type **Desktop app**.
5. Download the JSON credentials.
6. Rename the file to `credentials.json`.
7. Put it in this project's root folder.

For a personal Gmail/test app, configure the app for external users/testing
and add your own Google account as a test user if Google asks you to.

The first time you click **Create Gmail Draft**, a browser authorization
window should open. After authorization, this app stores a local `token.json`.

`credentials.json`, `token.json`, and `.env` are intentionally ignored by Git.

## Safety / product behavior

- The Gmail function uses `users.drafts.create`.
- It does not call `messages.send` or `drafts.send`.
- You remain responsible for reviewing and sending each message.
