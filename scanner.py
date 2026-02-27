import os, re, json, requests, random, socket
from concurrent.futures import ThreadPoolExecutor
try:
    from google import genai
except ImportError: pass

def get_gemini_key():
    return os.getenv('GEMINI_API_KEY')

def load_channels(path):
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return ["v2ray_collector", "vpn_telegram_vless"]

def fetch_new_channels(api_key, existing):
    if not api_key: return existing
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='Generate 20 active public Telegram channel names for VLESS configs. Format: @name'
        )
        found = re.findall(r'@(\\w+)', response.text)
        return list(set(existing + found))
    except: return existing

def scrape_vless(channels):
    collected = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for ch in channels:
        try:
            r = requests.get(f"https://t.me/s/{ch}", timeout=10, headers=headers)
            if r.status_code == 200:
                collected.extend(re.findall(r'vless://[a-zA-Z0-9%@&?#=_.:/\\\\-]+', r.text))
        except: continue
    return list(set(collected))

def is_tcp_alive(proxy_uri):
    try:
        match = re.search(r"vless://[^@]+@([^:]+):(\\d+)", proxy_uri)
        if not match: return False
        host, port = match.group(1), int(match.group(2))
        with socket.create_connection((host, port), timeout=1.5): return True
    except: return False

def run():
    channels = load_channels("telegram_channels.json")
    if random.random() < 0.4:
        key = get_gemini_key()
        channels = fetch_new_channels(key, channels)
        with open("telegram_channels.json", 'w') as f: json.dump(sorted(list(set(channels))), f, indent=2)
    raw_vless = scrape_vless(channels)
    valid_vless = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(is_tcp_alive, raw_vless))
        for i, alive in enumerate(results):
            if alive: valid_vless.append(raw_vless[i])
    with open("live_configs.txt", "w") as f: f.write("\\n".join(valid_vless))

if __name__ == "__main__":
    run()