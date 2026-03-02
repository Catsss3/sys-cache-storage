import os, re, requests, base64, json
from concurrent.futures import ThreadPoolExecutor

SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"

def decode_base64(text):
    try:
        return base64.b64decode(text.strip() + '=' * (-len(text.strip()) % 4)).decode('utf-8', errors='ignore')
    except: return text

def scrape_source(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=20, headers=headers)
        if r.status_code != 200: return []
        
        content = r.text
        # Если это подписка, пробуем декод
        if not content.strip().startswith('hy2://'):
            content = decode_base64(content)
            
        return re.findall(r'hy2://[a-zA-Z0-9%@&?#=_.:/\\-]+', content)
    except: return []

def run():
    # Собираем источники из файла
    targets = []
    if os.path.exists(SOURCE_FILE):
        with open(SOURCE_FILE, 'r') as f:
            try:
                data = json.load(f)
                targets = data if isinstance(data, list) else []
            except: pass
    
    # Резервные "жирные" источники, если JSON пустой
    backup = ["https://raw.githubusercontent.com/vless-subscribe/v2ray/main/v2ray", 
              "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.txt"]
    targets = list(set(targets + backup))

    all_hy2 = []
    with ThreadPoolExecutor(max_workers=30) as ex:
        results = list(ex.map(scrape_source, targets))
        for res in results: all_hy2.extend(res)
    
    unique_hy2 = list(set(all_hy2))
    
    # Сохраняем ВСЁ найденное без "убийственной" проверки портов
    if unique_hy2:
        with open(OUTPUT_FILE, "w", encoding='utf-8') as f: 
            f.write("\n".join(unique_hy2))
        print(f"📡 Стелла собрала {len(unique_hy2)} Hy2 конфигов!")
    else:
        print("😢 Ничего не найдено даже в элитных источниках.")

if __name__ == '__main__': run()
