import json, os, requests, re, time

def discover():
    file_path = 'telegram_channels.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        channels_set = set(json.load(f))

    print(f"🔎 База до поиска: {len(channels_set)}")
    new_found = 0

    # --- 1. ПОИСК ЧЕРЕЗ DUCKDUCKGO (Без API ключей) ---
    print("🦆 Ищем через DuckDuckGo...")
    search_queries = ['site:t.me "proxy"', 'site:t.me "vless"', 'site:t.me "hysteria2"']
    for q in search_queries:
        try:
            url = f"https://duckduckgo.com/html/?q={q}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=15)
            links = re.findall(r't\.me/[a-zA-Z0-9_+]{5,}', res.text)
            for l in links:
                full = "https://" + l
                if full not in channels_set:
                    channels_set.add(full); new_found += 1
        except: continue

    # --- 2. ПОИСК ПО GITHUB GISTS (Последние обновленные) ---
    print("🐙 Ищем в GitHub Gists...")
    try:
        # Ищем gists с упоминанием прокси
        res = requests.get("https://api.github.com/search/code?q=t.me+extension:txt+vless", 
                           headers={'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'} if os.getenv("GITHUB_TOKEN") else {})
        # Для простоты берем прямые линки на выдачу
        gist_links = re.findall(r't\.me/[a-zA-Z0-9_+]{5,}', res.text)
        for l in gist_links:
            full = "https://" + l
            if full not in channels_set:
                channels_set.add(full); new_found += 1
    except: pass

    # --- 3. ПАРСИНГ ЖИВЫХ ТЕЛЕГРАМ-АГРЕГАТОРОВ ---
    print("📡 Парсим агрегаторы...")
    collectors = [
        "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/README.md",
        "https://raw.githubusercontent.com/m0neer/Proxy-List/main/README.md"
    ]
    for c in collectors:
        try:
            res = requests.get(c, timeout=15)
            links = re.findall(r't\.me/[a-zA-Z0-9_+]{5,}', res.text)
            for l in links:
                full = "https://" + l
                if full not in channels_set:
                    channels_set.add(full); new_found += 1
        except: continue

    # СОХРАНЕНИЕ
    final_list = sorted(list(channels_set))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Стелла нашла новых: {new_found}")
    print(f"📊 Итого в обойме: {len(final_list)}")

if __name__ == '__main__':
    discover()