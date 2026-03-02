import os, re, requests, socket
from concurrent.futures import ThreadPoolExecutor

SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"

def load_targets(path):
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f: content = f.read()
    raw_urls = re.findall(r'https?://[^\s,"\'\]]+', content)
    urls = []
    for u in raw_urls: urls.extend([p for p in re.split(r'(?=https://)', u) if p])
    words = re.findall(r'[\w\d_-]{4,}', content)
    exclude = ['https', 'http', 'github', 'raw', 'master', 'main', 'json', 'yaml']
    targets = list(set(urls))
    for w in words:
        if w.lower() not in exclude and not any(w in u for u in urls):
            targets.append(f"https://t.me/s/{w}")
    return list(set(targets))

def scrape_hy2(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return re.findall(r'hy2://[a-zA-Z0-9%@&?#=_.:/\\-]+', r.text)
    except: pass
    return []

def is_hy2_alive(uri):
    try:
        match = re.search(r"hy2://[^@]+@([^:]+):(\d+)", uri)
        if not match: return False
        host, port = match.group(1), int(match.group(2))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.8)
        s.sendto(b'', (host, port))
        s.close()
        return True
    except: return False

def run():
    print("📡 Охота за Hy2 началась...")
    targets = load_targets(SOURCE_FILE)
    raw_configs = []
    with ThreadPoolExecutor(max_workers=40) as ex:
        results = list(ex.map(scrape_hy2, targets))
        for res in results: raw_configs.extend(res)
    unique_hy2 = list(set(raw_configs))
    live_hy2 = []
    with ThreadPoolExecutor(max_workers=100) as ex:
        checks = list(ex.map(is_hy2_alive, unique_hy2))
        live_hy2 = [unique_hy2[i] for i, ok in enumerate(checks) if ok]
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f: f.write("\n".join(live_hy2))
    print(f"✅ Найдено живых Hy2: {len(live_hy2)}")

if __name__ == '__main__': run()
