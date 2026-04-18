
import json, os, re, time, random
from pathlib import Path
import requests

FILE_PATH = Path("telegram_channels.json")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
TIMEOUT = 25

# Используем raw-строки для регулярок, чтобы не было SyntaxWarning
TG_PATTERN = re.compile(r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_+]{5,}")
# Исправленная регулярка для поиска ссылок
SUB_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+(?:sub|subscribe|api/v1/client/subscribe)\?[^\s<>\"']+")

def fetch(url, params=None, headers=None, method='GET', json_data=None):
    hdr = {"User-Agent": "Mozilla/5.0"}
    try:
        if method == 'POST': return requests.post(url, json=json_data, timeout=TIMEOUT)
        return requests.get(url, params=params, timeout=TIMEOUT)
    except: return None

def gemini_search():
    if not GEMINI_KEY: return set()
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    queries = ['v2ray subscription link 2026', 'vless reality sub github', 'hysteria2 config t.me']
    found_links = set()
    for q in queries:
        payload = {"contents": [{"parts": [{"text": f"Search the web for {q} and list ONLY raw URLs of subscriptions or TG channels, one per line."}]}]}
        resp = fetch(endpoint, method='POST', json_data=payload)
        if resp and resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Вытаскиваем все подходящие ссылки
            found_links.update(re.findall(r'https?://[^\s<>\"\'\)]+', text))
            for m in TG_PATTERN.findall(text):
                found_links.add("https://" + m)
    return found_links

def main():
    if FILE_PATH.is_file():
        with open(FILE_PATH, "r") as f: data = set(json.load(f))
    else: data = set()
    
    print(f"🔎 База до: {len(data)}")
    new_found = gemini_search()
    
    final_data = sorted(list(data | new_found))
    print(f"✨ Нашла новых: {len(final_data) - len(data)}")
    
    with open(FILE_PATH, "w") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    print(f"📊 Итого: {len(final_data)}")

if __name__ == '__main__':
    main()
