import os, re, requests, socket, base64
from concurrent.futures import ThreadPoolExecutor

SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"

def decode_base64(text):
    try:
        return base64.b64decode(text + '=' * (-len(text) % 4)).decode('utf-8', errors='ignore')
    except: return text

def scrape_source(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=15, headers=headers)
        if r.status_code != 200: return []
        
        content = r.text
        # Если это подписка (начинается не с протокола, а с каши) - пробуем декод
        if not content.startswith(('hy2://', 'vless://', 'http')):
            content = decode_base64(content)
            
        return re.findall(r'hy2://[a-zA-Z0-9%@&?#=_.:/\\-]+', content)
    except: return []

def is_hy2_alive(uri):
    try:
        match = re.search(r"hy2://[^@]+@([^:]+):(\d+)", uri)
        if not match: return False
        host, port = match.group(1), int(match.group(2))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.5)
        s.sendto(b'\x00', (host, port))
        s.close()
        return True
    except: return False

def run():
    if not os.path.exists(SOURCE_FILE): return
    with open(SOURCE_FILE, 'r') as f: targets = json.load(f)
    
    # ТГ ссылки преобразуем в /s/ формат
    final_targets = []
    for t in targets:
        if 't.me/' in t and '/s/' not in t:
            final_targets.append(t.replace('t.me/', 't.me/s/'))
        else: final_targets.append(t)

    all_hy2 = []
    with ThreadPoolExecutor(max_workers=50) as ex:
        results = list(ex.map(scrape_source, final_targets))
        for res in results: all_hy2.extend(res)
    
    unique_hy2 = list(set(all_hy2))
    live_hy2 = []
    with ThreadPoolExecutor(max_workers=100) as ex:
        checks = list(ex.map(is_hy2_alive, unique_hy2))
        live_hy2 = [unique_hy2[i] for i, ok in enumerate(checks) if ok]

    with open(OUTPUT_FILE, "w") as f: f.write("\n".join(live_hy2))
    print(f"📡 Найдено живых Hy2: {len(live_hy2)}")

if __name__ == '__main__': 
    import json
    run()
