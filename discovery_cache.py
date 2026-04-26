
import json, os, re, time, random
from pathlib import Path
import requests
from urllib.parse import unquote

FILE_PATH = Path("telegram_channels.json")
GITHUB_TOKEN = os.getenv("WORKFLOW_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

TIMEOUT = 25
# 1. ПУЛ USER-AGENT ДЛЯ СКРЫТНОСТИ
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
]

TG_PATTERN = re.compile(r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_+]{5,}")
SUB_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+(?:sub|subscribe|api/v1/client/subscribe)\?[^\s<>\"']+")

# 2. УЛУЧШЕННЫЙ ПАРСИНГ И НОРМАЛИЗАЦИЯ
def normalize_url(url):
    try:
        url = unquote(url.strip())
        if not url.startswith(("http://", "https://")):
            url = "https://" + url.lstrip("/")
        # Убираем лишние слеши в конце
        return url.rstrip("/")
    except:
        return url

def fetch(url, params=None, headers=None, method="GET", json_data=None):
    hdr = {"User-Agent": random.choice(UA_POOL)}
    try:
        if method == "POST":
            return requests.post(url, json=json_data, headers=hdr, timeout=TIMEOUT)
        return requests.get(url, params=params, headers=hdr, timeout=TIMEOUT)
    except: return None

def extract_links(html):
    ch = {normalize_url(f"https://{m}") for m in TG_PATTERN.findall(html)}
    sub = {normalize_url(s) for s in SUB_URL_PATTERN.findall(html)}
    return ch, sub

# 3. УМНЫЙ GEMINI С JSON-ФОРМАТОМ
def gemini_search():
    if not GEMINI_KEY: return set(), set()
    queries = [
        'newest V2Ray/VLESS reality subscription links April 2026',
        'active telegram channels sharing v2ray configs 2026',
        'raw github user content v2ray sub txt',
        'hysteria2 nodes configuration list'
    ]
    new_ch, new_sub = set(), set()
    print("💎 Стелла: Умный Gemini-парсинг...")
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    for q in queries:
        prompt = f"Find unique active URLs (t.me or subscription links) for: {q}. Return ONLY a clean list of URLs, one per line."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = fetch(endpoint, method="POST", json_data=payload)
        if resp and resp.status_code == 200:
            try:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                c, s = extract_links(text)
                new_ch.update(c); new_sub.update(s)
            except: continue
        time.sleep(2)
    return new_ch, new_sub

def github_code_search():
    if not GITHUB_TOKEN: return set()
    new_sub = set()
    print("🐙 Стелла: Глубокий GitHub поиск (5 страниц)...")
    url = "https://api.github.com/search/code"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    for page in range(1, 6):
        params = {"q": "v2ray sub in:url extension:txt", "per_page": 30, "page": page}
        resp = fetch(url, params=params, headers=headers)
        if resp and resp.status_code == 200:
            items = resp.json().get("items", [])
            for item in items:
                raw = item.get("html_url", "").replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                new_sub.add(normalize_url(raw))
        else: break
        time.sleep(random.uniform(2, 4))
    return new_sub

def get_gists():
    new_sub = set()
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    resp = fetch("https://api.github.com/gists/public", headers=headers)
    if resp and resp.status_code == 200:
        for gist in resp.json()[:30]:
            for fn, fdata in gist.get("files", {}).items():
                if any(k in fn.lower() for k in ("sub", "v2ray", "proxy")):
                    if fdata.get("raw_url"): new_sub.add(normalize_url(fdata.get("raw_url")))
    return new_sub

def tg_web_crawl():
    # Расширил список агрегаторов
    aggregators = ["proxylistdaily", "v2raycollector", "v2ray_free_conf", "v2ray_alpha", "VlessVpns", "v2ray_vpn_config"]
    new_ch, new_sub = set(), set()
    for channel in aggregators:
        url = f"https://t.me/s/{channel}"
        resp = fetch(url)
        if resp:
            c, s = extract_links(resp.text)
            new_ch.update(c); new_sub.update(s)
    return new_ch, new_sub

def main():
    if FILE_PATH.is_file():
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            try: existing = set(json.load(f))
            except: existing = set()
    else: existing = set()

    print(f"🔎 База до: {len(existing)}")
    
    g_ch, g_sub = gemini_search()
    gists = get_gists()
    gh_code = github_code_search()
    tw_ch, tw_sub = tg_web_crawl()
    
    # Склеиваем и нормализуем всё финально
    all_found = {link for link in (existing | g_ch | g_sub | gists | gh_code | tw_ch | tw_sub) if link}
    
    added_count = len(all_found) - len(existing)
    print(f"✨ Итог: добавлено {added_count} новых.")
    
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(all_found)), f, indent=2, ensure_ascii=False)
    print(f"📊 Всего в обойме: {len(all_found)}")

if __name__ == "__main__":
    main()
