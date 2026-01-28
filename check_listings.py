import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

EMAIL_TO = "stipe.skroce@gmail.com"
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

SEEN_FILE = "seen_listings.json"

URLS = [
    "https://www.njuskalo.hr/prodaja-stanova?geo%5BlocationIds%5D=2685%2C2686&livingArea%5Bmin%5D=70",
    "https://www.njuskalo.hr/iznajmljivanje-stanova?geo%5BlocationIds%5D=2685%2C2686&livingArea%5Bmin%5D=70",
    "https://www.njuskalo.hr/prodaja-kuca?geo%5BlocationIds%5D=2685%2C2686&livingArea%5Bmin%5D=70",
    "https://www.njuskalo.hr/iznajmljivanje-kuca?geo%5BlocationIds%5D=2685%2C2686&livingArea%5Bmin%5D=70",
    "https://www.nekretnine.hr/prodaja-stambene-nekretnine/zagreb/utrina-travno-sopot/?superficieMinima=60"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Mail poslan.")
    except Exception as e:
        print("Greška pri slanju maila:", e)

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def fetch_listings(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/oglas/" in href:
            if href.startswith("/"):
                href = "https://www.njuskalo.hr" + href
            links.add(href)

        if "nekretnine.hr/nekretnina/" in href:
            links.add(href)

    return links

def main():
    seen = load_seen()
    new_found = []

    for url in URLS:
        try:
            listings = fetch_listings(url)
            for l in listings:
                if l not in seen:
                    new_found.append(l)
                    seen.add(l)
        except Exception as e:
            print("Greška kod", url, e)

    if new_found:
        body = "Pronađeni su novi oglasi:\n\n"
        for l in new_found:
            body += l + "\n"

        send_email("🏠 Novi oglasi za nekretnine", body)
        save_seen(seen)
    else:
        print("Nema novih oglasa.")

if __name__ == "__main__":
    main()
