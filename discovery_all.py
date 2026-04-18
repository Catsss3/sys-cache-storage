
import json, os, re, time, random
from pathlib import Path
import requests

FILE_PATH = Path("telegram_channels.json")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
TIMEOUT = 30

TG_PATTERN = re.compile(r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_+]{5,}")
SUB_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+(?:sub|subscribe|api/v1/client/subscribe)\?[^\s<>\"']+")

def fetch(url, params=None, headers=None, method='GET', json_data=None):
    hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        if method == 'POST': return requests.post(url, json=json_data, timeout=TIMEOUT)
        return requests.get(url, params=params, headers=hdr, timeout=TIMEOUT)
    except: return None

def gemini_search():
    if not GEMINI_KEY: return set()
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    # ТЕ САМЫЕ РАСШИРЕННЫЕ ЗАПРОСЫ
    queries = [
        'latest v2ray subscription base64 2026',
        'free vless reality configs telegram links',
        'site:github.com "index of" v2ray sub',
        'node share link vless trojan hysteria2',
        'clash meta subscription link free list',
        'v2ray sub link github 2026 subscribe',
        'daily updated vpn subscription link'
    ]
    
    found_links = set()
    print(f"💎 Стелла копает Gemini API по {len(queries)} направлениям...")
    
    for q in queries:
        payload = {"contents": [{"parts": [{"text": f"Act as a web scraper. Search the web for '{q}' and return a PLAIN TEXT LIST of unique URLs (v2ray subs or TG channels). ONLY URLs, no text."}]}]}
        resp = fetch(endpoint, method='POST', json_data=payload)
        if resp and resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Вытаскиваем все ссылки
            found_links.update(re.findall(r'https?://[^\s<>\"\'\)]+', text))
            for m in TG_PATTERN.findall(text):
                found_links.add("https://" + m)
        time.sleep(2)
    return found_links

def main():
    if FILE_PATH.is_file():
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            try: data = set(json.load(f))
            except: data = set()
    else: data = set()
    
    print(f"🔎 База до: {len(data)}")
    
    # Запуск поиска
    new_found = gemini_search()
    
    # Фильтруем и объединяем
    final_data = sorted(list(data | new_found))
    print(f"✨ Нашла новых уникальных линков: {len(final_data) - len(data)}")
    
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    print(f"📊 Итого в обойме: {len(final_data)}")

if __name__ == '__main__':
    main()
