import os, re, requests, base64, json
from concurrent.futures import ThreadPoolExecutor

SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"

def decode_base64(text):
    try:
        # Убираем пробелы и лишние символы перед декодом
        clean_text = re.sub(r'[^a-zA-Z0-9+/=]', '', text.strip())
        return base64.b64decode(clean_text + '=' * (-len(clean_text) % 4)).decode('utf-8', errors='ignore')
    except: return text

def scrape_source(url):
    try:
        print(f"📡 Проверяю: {url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=25, headers=headers)
        if r.status_code != 200: 
            print(f"❌ Ошибка {r.status_code} на {url}")
            return []
        
        raw_content = r.text
        # Ищем Hy2 сразу в сыром виде
        found = re.findall(r'hy2://[^\s,"\'\]]+', raw_content)
        
        # Если не нашли, пробуем декодировать всё подряд (Base64)
        if not found:
            decoded = decode_base64(raw_content)
            found = re.findall(r'hy2://[^\s,"\'\]]+', decoded)
            
        if found: print(f"✅ Найдено {len(found)} конфигов на {url}")
        return found
    except Exception as e:
        print(f"⚠️ Ошибка на {url}: {e}")
        return []

def run():
    # Хардкод источников прямо в скрипт, чтобы не зависеть от JSON
    targets = [
        "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.txt",
        "https://raw.githubusercontent.com/vless-subscribe/v2ray/main/v2ray",
        "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/v2",
        "https://raw.githubusercontent.com/Pawf3x/Free-Vpn-Configs/main/All_Configs_Sub.txt",
        "https://raw.githubusercontent.com/LonUp/NodeList/main/v2ray/v2ray.txt",
        "https://raw.githubusercontent.com/MoYuanJun/Free-Proxy/master/sub"
    ]
    
    # Плюс добавляем из JSON если он есть
    if os.path.exists(SOURCE_FILE):
        try:
            with open(SOURCE_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list): targets.extend(data)
        except: pass

    targets = list(set(targets))
    print(f"🚀 Начинаю поиск по {len(targets)} источникам...")

    all_hy2 = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        results = list(ex.map(scrape_source, targets))
        for res in results: all_hy2.extend(res)
    
    unique_hy2 = list(set(all_hy2))
    
    if unique_hy2:
        with open(OUTPUT_FILE, "w", encoding='utf-8') as f: 
            f.write("\n".join(unique_hy2))
        print(f"🎉 ПОБЕДА! Собрано {len(unique_hy2)} Hy2 конфигов!")
    else:
        print("💀 Глухо. Hy2 в этих источниках сейчас нет.")

if __name__ == '__main__': run()
