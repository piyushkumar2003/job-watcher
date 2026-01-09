import os, json, hashlib, re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from supabase import create_client
from playwright.sync_api import sync_playwright

load_dotenv()

# ENV
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    })

def fetch_html(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "job-watcher-bot"})
        if r.status_code == 200:
            return r.text
    except:
        pass

    # fallback to JS rendering
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()
        return html

def seen(fp):
    res = sb.table("seen_jobs").select("id").eq("fingerprint", fp).execute()
    return len(res.data) > 0

def save(fp, url, title, company):
    sb.table("seen_jobs").insert({
        "fingerprint": fp,
        "url": url,
        "title": title,
        "company": company
    }).execute()

def run():
    config = json.load(open("config.json"))
    new_jobs = []

    for job in config["jobs"]:
        html = fetch_html(job["url"])
        soup = BeautifulSoup(html, "html.parser")

        for kw in job["keywords"]:
            regex = re.compile(rf"\b{re.escape(kw)}\b", re.I)
            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True)
                if regex.search(text):
                    link = urljoin(job["url"], a["href"])
                    fp = sha256(link)

                    if not seen(fp):
                        save(fp, link, text, job["company"])
                        new_jobs.append((job["company"], text, link))

    if new_jobs:
        msg = "🔥 *New Job Openings Found*\n\n"
        for c, t, l in new_jobs:
            msg += f"🏢 {c}\n📌 {t}\n🔗 {l}\n\n"
        send_telegram(msg)

if __name__ == "__main__":
    run()
