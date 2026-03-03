import os, re, requests, json

def is_reality(link):
    # Проверяем, есть ли признаки Reality
    if "vless://" in link:
        return "security=reality" in link or "pbk=" in link
    return True # Hy2 пропускаем всегда

def run():
    SOURCE_FILE = "telegram_channels.json"
    if not os.path.exists(SOURCE_FILE): return

    with open(SOURCE_FILE, "r") as f:
        sources = json.load(f)
    
    results = []
    print(f"📡 Стелла включает VIP-фильтр по {len(sources)} источникам...")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    for url in sources:
        try:
            target = url.replace('t.me/', 't.me/s/') if 't.me' in url else url
            r = requests.get(target, headers=headers, timeout=10)
            if r.status_code == 200:
                # Первичный сбор всех Hy2 и Vless
                raw_found = re.findall(r'(hy2://[^\s<"\'\]#]+|vless://[^\s<"\'\]#]+)', r.text)
                
                # Фильтруем: оставляем только Hy2 и Reality
                for link in raw_found:
                    if is_reality(link):
                        results.append(link)
                
                # Заглядываем в подписки (там часто самый сок Reality)
                subs = re.findall(r'https?://[^\s<"\'\]]+/(?:sub|subscribe)\?[^\s<"\'\]]+', r.text)
                for s_url in subs[:2]:
                    try:
                        sr = requests.get(s_url, timeout=7)
                        s_raw = re.findall(r'(hy2://[^\s<"\'\]#]+|vless://[^\s<"\'\]#]+)', sr.text)
                        for s_link in s_raw:
                            if is_reality(s_link):
                                results.append(s_link)
                    except: continue
        except: continue

    unique = sorted(list(set(results)))
    with open("live_configs.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(unique))
    
    print(f"🎉 VIP-ИТОГ: Собрано {len(unique)} элитных конфигов (Hy2 + Reality)!")

if __name__ == '__main__': run()
