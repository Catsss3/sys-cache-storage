
import json, os, re, time, random
from pathlib import Path
import requests

FILE_PATH = Path("telegram_channels.json")
GITHUB_TOKEN = os.getenv("WORKFLOW_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

TIMEOUT = 25
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

TG_PATTERN = re.compile(r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_+]{5,}")
SUB_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+(?:sub|subscribe|api/v1/client/subscribe)\?[^\s<>\"']+")

def fetch(url, params=None, headers=None, method="GET", json_data=None):
    hdr = {"User-Agent": USER_AGENT}
    try:
        if method == "POST":
            return requests.post(url, json=json_data, headers=hdr, timeout=TIMEOUT)
        return requests.get(url, params=params, headers=hdr, timeout=TIMEOUT)
    except: return None

def extract_links(html):
    ch = {f"https://{m}" for m in TG_PATTERN.findall(html)}
    sub = set(SUB_URL_PATTERN.findall(html))
    return ch, sub

def gemini_search():
    if not GEMINI_KEY: return set(), set()
    # Умные запросы с привязкой к дате
    queries = [
        'latest vless reality subscription April 2026',
        'active telegram channels proxy v2ray configs 2026',
        'github raw link v2ray subscription list',
        'new hysteria2 nodes telegram',
        'v2ray nodes subscription github links'
    ]
    new_ch, new_sub = set(), set()
    print("💎 Стелла: Глубокий поиск Gemini (Smart Queries)...")
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    for q in queries:
        payload = {"contents": [{"parts": [{"text": f"Find unique active URLs (t.me or subs) for {q}. Return raw list only."}]}]}
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
    print("🐙 Стелла: Глубокий поиск по GitHub (Пагинация 5 страниц)...")
    url = "https://api.github.com/search/code"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    for page in range(1, 6):
        params = {"q": "sub in:url extension:txt", "per_page": 30, "page": page}
        resp = fetch(url, params=params, headers=headers)
        if resp and resp.status_code == 200:
            items = resp.json().get("items", [])
            for item in items:
                raw = item.get("html_url", "").replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                new_sub.add(raw)
            print(f"   [GitHub] Страница {page} - готово.")
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
                    if fdata.get("raw_url"): new_sub.add(fdata.get("raw_url"))
    return new_sub

def tg_web_crawl():
    aggregators = ["proxylistdaily", "v2raycollector", "v2ray_free_conf", "v2ray_alpha", "VlessVpns"]
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
    
    all_found = {link.strip() for link in (existing | g_ch | g_sub | gists | gh_code | tw_ch | tw_sub) if link.strip()}
    
    print(f"✨ Итог: добавлено {len(all_found) - len(existing)} новых.")
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(all_found)), f, indent=2, ensure_ascii=False)
    print(f"📊 Всего в обойме: {len(all_found)}")

if __name__ == "__main__":
    main()
