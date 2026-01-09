# Job Watcher

An automated job monitoring agent that periodically checks company career pages for specific job roles and sends **Telegram notifications** when new matching job openings are posted.

This project is designed to be:

* ✅ Fully automated (runs every 3 hours)
* ✅ Free to run (uses GitHub Actions)
* ✅ Deterministic & reliable (no unnecessary LLM usage)
* ✅ Secure (uses GitHub Secrets)

---

## Features

* Monitor **multiple company career pages**
* Match **exact job keywords** (e.g. `Software Engineer`)
* Deduplicate results (never notifies the same job twice)
* Telegram notifications for new job postings
* Runs automatically every 3 hours via GitHub Actions
* No server or laptop required to stay online

---

## Tech Stack

* **Python 3.9+**
* **Requests / BeautifulSoup** – Web scraping
* **Supabase (PostgreSQL)** – Deduplication storage
* **Telegram Bot API** – Notifications
* **GitHub Actions** – Scheduling & execution

---

## Project Structure

```
job-watcher/
├── monitor.py          # Main job monitoring script
├── config.json         # Companies, URLs, and job keywords
├── requirements.txt    # Python dependencies
├── .gitignore          # Ignored files
└── .github/workflows/
    └── job_watcher.yml # GitHub Actions workflow
```

---

## How It Works

Every 3 hours:

1. GitHub Actions spins up a fresh runner
2. `monitor.py` fetches each career page URL
3. Searches page content for provided keywords
4. Generates a unique fingerprint for each job post
5. Checks Supabase to avoid duplicates
6. Sends a Telegram message if a new job is found
7. Exits cleanly

---

## Setup Guide (Step-by-Step)

### 1️⃣ Fork or Clone the Repository

```bash
git clone https://github.com/<your-username>/job-watcher.git
cd job-watcher
```

---

### 2️⃣ Create a Telegram Bot

1. Open Telegram
2. Search for **@BotFather**
3. Run `/start` → `/newbot`
4. Save:

   * **Bot Token**
5. Send a message to your bot
6. Get your **Chat ID** using:

   * [https://api.telegram.org/bot](https://api.telegram.org/bot)<BOT_TOKEN>/getUpdates

---

### 3️⃣ Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Create a new project
3. Create a table:

```sql
create table job_posts (
  id uuid default uuid_generate_v4() primary key,
  fingerprint text unique,
  created_at timestamp default now()
);
```

4. Save:

   * `SUPABASE_URL`
   * `SUPABASE_KEY`

---

### 4️⃣ Configure `config.json`

Edit `config.json`:

```json
{
  "jobs": [
    {
      "company": "Google",
      "url": "https://careers.google.com/jobs/results/",
      "keywords": ["software engineer"]
    }
  ]
}
```

You can add multiple companies and keywords.

---

### 5️⃣ Add GitHub Secrets

Go to:

**GitHub Repo → Settings → Secrets → Actions → New repository secret**

Add the following:

| Name                 | Value                     |
| -------------------- | ------------------------- |
| `SUPABASE_URL`       | Your Supabase project URL |
| `SUPABASE_KEY`       | Supabase anon/service key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token        |
| `TELEGRAM_CHAT_ID`   | Your Telegram chat ID     |

---

### 6️⃣ GitHub Actions Workflow

Ensure this file exists:

`.github/workflows/job_watcher.yml`

```yaml
name: Job Watcher

on:
  schedule:
    - cron: '0 */3 * * *'
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python monitor.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

---

## ▶️ Running Locally (Optional)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python monitor.py
```

---

## Notification Example

```
🆕 New Job Found!
Company: Google
Keyword: Software Engineer
Link: https://careers.google.com/jobs/results/123456
```

---

## Security

* Secrets are never committed
* Credentials stored in GitHub Secrets
* Fresh runner on every execution

---

## Future Improvements

* Semantic job relevance scoring (LLM)
* Resume-to-job fit analysis
* Support for Greenhouse / Lever APIs
* Slack / Discord notifications
* Web dashboard

---

## License

MIT License

---

## Author

Built by **Piyush Kumar**

If you find this useful, ⭐ the repo!
