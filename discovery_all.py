
import json, os, re, time, random
from pathlib import Path
import requests

FILE_PATH = Path("telegram_channels.json")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# ВОЗВРАЩАЕМ ТЕ САМЫЕ РЕГУЛЯРКИ, КОТОРЫЕ НАШЛИ +7
TG_PATTERN = re.compile(r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_+]{5,}")
SUB_URL_PATTERN = re.compile(r"https?://[^\s<>\"']+(?:sub|subscribe|api/v1/client/subscribe)\?[^\s<>\"']+")

def fetch_gemini(query):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"List ONLY raw URLs of v2ray/vless/hysteria2 subscriptions or Telegram channels for query: {query}. No talk, just URLs."}]}]
    }
    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"] if resp.status_code == 200 else ""
    except: return ""

def main():
    if FILE_PATH.is_file():
        with open(FILE_PATH, "r", encoding="utf-8") as f: data = set(json.load(f))
    else: data = set()
    
    print(f"🔎 База до: {len(data)}")
    
    queries = [
        'v2ray subscription link april 2026',
        'vless reality t.me channels',
        'hysteria2 nodes github gist',
        'free shadowsocks subscription 2026'
    ]
    
    new_found = set()
    for q in queries:
        print(f"📡 Поиск по: {q}")
        text = fetch_gemini(q)
        
        # 1. Ищем строгие подписки (те самые +7)
        for link in SUB_URL_PATTERN.findall(text):
            new_found.add(link)
        
        # 2. Ищем каналы
        for m in TG_PATTERN.findall(text):
            new_found.add("https://" + m)
            
    initial_size = len(data)
    data.update(new_found)
    print(f"✨ Нашла новых уникальных: {len(data) - initial_size}")
    
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(data)), f, indent=2, ensure_ascii=False)
    print(f"📊 Итого в базе: {len(data)}")

if __name__ == '__main__':
    main()
