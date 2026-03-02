import os, re, requests, base64

OUTPUT_FILE = "live_configs.txt"

def scrape_tg(channel):
    try:
        url = f"https://t.me/s/{channel}"
        r = requests.get(url, timeout=15)
        return re.findall(r'hy2://[^\s,"\'\]]+', r.text)
    except: return []

def scrape_direct(url):
    try:
        # Используем прокси-зеркало для обхода 404 (jsDelivr)
        mirror_url = url.replace("raw.githubusercontent.com", "fastly.jsdelivr.net/gh").replace("/main/", "@main/")
        r = requests.get(mirror_url, timeout=15)
        if r.status_code == 200:
            content = r.text
            # Если база в base64
            if "hy2://" not in content:
                try:
                    content = base64.b64decode(content.strip()).decode('utf-8')
                except: pass
            return re.findall(r'hy2://[^\s,"\'\]]+', content)
    except: pass
    return []

def run():
    # ТОЛЬКО САМЫЕ ЖИРНЫЕ ИСТОЧНИКИ (Через зеркала)
    sources = [
        "https://raw.githubusercontent.com/freev2rayconfig/v2ray/main/hysteria2",
        "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2ray"
    ]
    
    # ТВОИ КАНАЛЫ (СПИСОК ВРУЧНУЮ, ЧТОБЫ НЕ ЗАВИСЕТЬ ОТ JSON)
    channels = ["v2ray_free-v2ray", "v2ray_free_conf", "V2ray_Alpha", "v2rayNG_VPNH", "Hysteria2_Free"]

    print("🚜 Танк выехал на охоту...")
    results = []
    
    for s in sources:
        found = scrape_direct(s)
        if found: 
            print(f"✅ Найдено {len(found)} в источнике")
            results.extend(found)
            
    for c in channels:
        found = scrape_tg(c)
        if found: 
            print(f"✅ Найдено {len(found)} в канале {c}")
            results.extend(found)

    unique = list(set(results))
    if unique:
        with open(OUTPUT_FILE, "w") as f: f.write("\n".join(unique))
        print(f"🎉 Стелла нашла {len(unique)} конфигов!")
    else:
        print("💀 Пусто. Даже танк не проехал.")

if __name__ == '__main__': run()
