import json, os, requests, re, time

def discover():
    file_path = 'telegram_channels.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        channels_set = set(json.load(f))

    print(f"🔎 База до поиска: {len(channels_set)}")
    new_found = 0

    # Используем raw-строки для регулярок, чтобы не было Warning
    tg_pattern = r't\.me/[a-zA-Z0-9_+]{5,}'

    # --- 1. УСИЛЕННЫЙ ПОИСК DUCKDUCKGO ---
    print("🦆 Стелла уходит в глубокий поиск DuckDuckGo...")
    # Добавляем специфику: Hysteria2, Reality, Shadowsocks
    queries = [
        'site:t.me "hysteria2"', 
        'site:t.me "vless reality"', 
        'site:github.com "proxy list" extension:txt',
        'site:pastebin.com "vless://"'
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for q in queries:
        try:
            # Используем облегченную версию DDG для парсинга
            res = requests.get(f"https://duckduckgo.com/html/?q={q}", headers=headers, timeout=15)
            found = re.findall(tg_pattern, res.text)
            for l in found:
                full = "https://" + l
                if full not in channels_set:
                    channels_set.add(full); new_found += 1
            time.sleep(2) # Пауза, чтобы не забанили
        except: continue

    # --- 2. GITHUB GISTS & SEARCH ---
    print("🐙 Проверяем свежие Gists и репозитории...")
    # Поиск по заголовкам файлов в GitHub
    search_urls = [
        "https://api.github.com/search/repositories?q=vless+stars:>10&sort=updated",
        "https://api.github.com/search/repositories?q=proxy+collector&sort=updated"
    ]
    for url in search_urls:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            # Ищем любые упоминания t.me в описаниях или коде
            found = re.findall(tg_pattern, res.text)
            for l in found:
                full = "https://" + l
                if full not in channels_set:
                    channels_set.add(full); new_found += 1
        except: continue

    # СОХРАНЕНИЕ
    final_list = sorted(list(channels_set))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Стелла накопала новых: {new_found}")
    print(f"📊 Итоговая мощь: {len(final_list)} источников")

if __name__ == '__main__':
    discover()