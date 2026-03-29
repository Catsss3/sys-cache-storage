import json, os, requests, re, time, base64

def discover():
    file_path = 'telegram_channels.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        channels_set = set(json.load(f))

    print(f"🔎 База до поиска: {len(channels_set)}")
    new_found = 0
    tg_pattern = r't\.me/[a-zA-Z0-9_+]{5,}'
    # Паттерн для поиска ссылок-подписок
    sub_url_pattern = r'https?://[^\s<>"]+/(?:sub|subscribe|api/v1/client/subscribe)\?[^\s<>"]+'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # --- 1. ТВОЙ СТАРЫЙ ПОИСК (КАНАЛЫ) ---
    queries = ['site:t.me "hysteria2"', 'site:t.me "vless reality"', 'site:github.com "proxy list"']
    for q in queries:
        try:
            res = requests.get(f"https://duckduckgo.com/html/?q={q}", headers=headers, timeout=15)
            found = re.findall(tg_pattern, res.text)
            for l in found:
                full = "https://" + l
                if full not in channels_set:
                    channels_set.add(full); new_found += 1
        except: continue

    # --- 2. НОВЫЙ БЛОК: ОХОТА ЗА ПОДПИСКАМИ (GISTS & PASTEBIN) ---
    print("💎 Стелла ищет скрытые подписки...")
    sub_queries = [
        'site:github.com "sub/link" extension:txt',
        'site:pastebin.com "subscribe?token="',
        'site:gist.github.com "v2ray" "sub"'
    ]
    for q in sub_queries:
        try:
            res = requests.get(f"https://duckduckgo.com/html/?q={q}", headers=headers, timeout=15)
            # Ищем URL подписок
            subs = re.findall(sub_url_pattern, res.text)
            for s in subs:
                # Мы можем либо сохранить саму подписку, либо добавить её в базу каналов для парсинга
                if s not in channels_set:
                    channels_set.add(s); new_found += 1
        except: continue

    # СОХРАНЕНИЕ
    final_list = sorted(list(channels_set))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Стелла добавила новых источников (включая подписки): {new_found}")
    print(f"📊 Итого в обойме: {len(final_list)}")

if __name__ == '__main__':
    discover()