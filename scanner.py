import os, re, requests, base64, json
from concurrent.futures import ThreadPoolExecutor

SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"

def decode_base64(text):
    try:
        clean_text = re.sub(r'[^a-zA-Z0-9+/=]', '', text.strip())
        return base64.b64decode(clean_text + '=' * (-len(clean_text) % 4)).decode('utf-8', errors='ignore')
    except: return text

def scrape_source(url):
    try:
        print(f"📡 Проверяю: {url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=25, headers=headers)
        if r.status_code != 200: 
            print(f"❌ Ошибка {r.status_code}")
            return []
        
        content = r.text
        # Пробуем найти Hy2 сразу
        found = re.findall(r'hy2://[^\s,"\'\]]+', content)
        
        # Если пусто - декодируем (для подписок)
        if not found:
            decoded = decode_base64(content)
            found = re.findall(r'hy2://[^\s,"\'\]]+', decoded)
            
        if found: print(f"✅ Найдено {len(found)} Hy2!")
        return found
    except: return []

def run():
    # АКТУАЛЬНЫЕ ССЫЛКИ НА МАРТ 2026
    targets = [
        "https://raw.githubusercontent.com/freev2rayconfig/v2ray/main/v2ray",
        "https://raw.githubusercontent.com/freev2rayconfig/v2ray/main/hysteria2",
        "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2ray",
        "https://sub.hf.space/hysteria2", # Специальный API-агрегатор
        "https://v2rayfree.eu.org/hysteria2"
    ]
    
    # Добавляем ТГ каналы из JSON (только те, что /s/)
    if os.path.exists(SOURCE_FILE):
        try:
            with open(SOURCE_FILE, 'r') as f:
                data = json.load(f)
                for t in data:
                    if 't.me' in t:
                        targets.append(t.replace('t.me/', 't.me/s/'))
                    else: targets.append(t)
        except: pass

    targets = list(set(targets))
    all_hy2 = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(scrape_source, targets))
        for res in results: all_hy2.extend(res)
    
    unique_hy2 = list(set(all_hy2))
    
    if unique_hy2:
        with open(OUTPUT_FILE, "w", encoding='utf-8') as f: 
            f.write("\n".join(unique_hy2))
        print(f"🎉 Стелла нашла {len(unique_hy2)} живых Hy2!")
    else:
        print("💀 Даже новые ссылки молчат. Hy2 сегодня в дефиците.")

if __name__ == '__main__': run()
