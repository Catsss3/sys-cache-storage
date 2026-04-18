
import json, os, re, time, random
from pathlib import Path
import requests

FILE_PATH = Path("telegram_channels.json")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

TG_PATTERN = re.compile(r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_+]{5,}")

def fetch_gemini(query):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Find and list ONLY the latest working raw subscription URLs (v2ray, vless, hysteria2, reality) from GitHub Gists, Pastebin, and Telegram aggregators. Query: {query}. Return ONLY URLs, no descriptions."}]}]
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return ""
    return ""

def main():
    if FILE_PATH.is_file():
        with open(FILE_PATH, "r", encoding="utf-8") as f: data = set(json.load(f))
    else: data = set()
    
    print(f"🔎 База до: {len(data)}")
    
    # Сверх-агрессивные запросы на поиск "свежака"
    aggressive_queries = [
        'newly created v2ray subscription links April 2026',
        'raw.githubusercontent.com v2ray vless sub links',
        'site:github.com "v2ray" "update" "2026" "sub"',
        'hysteria2 reality configs telegram crawler',
        'vless reality node list April 2026'
    ]
    
    new_found = set()
    for q in aggressive_queries:
        print(f"🚀 Стелла пробивает: {q}")
        raw_text = fetch_gemini(q)
        # Ищем всё, что похоже на URL
        urls = re.findall(r'https?://[^\s<>\"\'\)]+', raw_text)
        new_found.update(urls)
        # Ищем каналы
        for m in TG_PATTERN.findall(raw_text):
            new_found.add("https://" + m)
        time.sleep(2)

    initial_size = len(data)
    data.update(new_found)
    
    print(f"✨ Нашла новых (до фильтрации): {len(data) - initial_size}")
    
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(data)), f, indent=2, ensure_ascii=False)
    print(f"📊 Итого: {len(data)}")

if __name__ == '__main__':
    main()
