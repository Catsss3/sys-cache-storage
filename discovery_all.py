
import json, os, re, time, random
from pathlib import Path
import requests

FILE_PATH = Path("telegram_channels.json")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TIMEOUT = 20
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

TG_PATTERN = re.compile(r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_+]{5,}")
SUB_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+/(?:sub|subscribe|api/v1/client/subscribe)\?[^\s<>\"']+")

def fetch(url, params=None, headers=None):
    hdr = {"User-Agent": USER_AGENT}
    if headers: hdr.update(headers)
    try:
        resp = requests.get(url, params=params, headers=hdr, timeout=TIMEOUT)
        return resp
    except: return None

def extract_links(html):
    ch = {f"https://{m}" for m in TG_PATTERN.findall(html)}
    sub = set(SUB_URL_PATTERN.findall(html))
    return ch, sub

def get_gists():
    new_sub = set()
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    resp = fetch("https://api.github.com/gists/public", headers=headers)
    if resp and resp.status_code == 200:
        for gist in resp.json()[:30]:
            for fn, fdata in gist.get("files", {}).items():
                if any(k in fn.lower() for k in ("sub", "v2ray", "proxy")):
                    raw = fdata.get("raw_url")
                    if raw: new_sub.add(raw)
    return new_sub

def github_code_search():
    if not GITHUB_TOKEN: return set()
    new_sub = set()
    url = "https://api.github.com/search/code"
    params = {"q": "sub in:url extension:txt extension:json", "per_page": 50}
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = fetch(url, params=params, headers=headers)
    if resp and resp.status_code == 200:
        for item in resp.json().get("items", []):
            raw = item.get("html_url", "").replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            new_sub.add(raw)
    return new_sub

def tg_web_crawl():
    aggregators = ["proxylistdaily", "v2raycollector", "v2ray_free_conf", "v2rayng_org", "v2ray_outline"]
    new_sub = set()
    for channel in aggregators:
        url = f"https://t.me/s/{channel}"
        resp = fetch(url)
        if resp:
            _, subs = extract_links(resp.text)
            new_sub.update(subs)
    return new_sub

def main():
    existing = set()
    if FILE_PATH.is_file():
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            existing = set(json.load(f))
    
    print(f"🔎 База до поиска: {len(existing)}")
    all_found = get_gists() | github_code_search() | tg_web_crawl()
    new_items = all_found - existing
    print(f"✨ Стелла нашла новых: {len(new_items)}")
    
    updated = sorted(list(existing | all_found))
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)
    print(f"📊 Итого в обойме: {len(updated)}")

if __name__ == '__main__':
    main()
