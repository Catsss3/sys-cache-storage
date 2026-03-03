import os
import re
import json
import socket
import requests
import concurrent.futures
from urllib.parse import urlparse

# --- Константы ---
SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"
MAX_WORKERS = 50
TCP_TIMEOUT = 3.0
REQUEST_TIMEOUT = 10
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def is_reality(link: str) -> bool:
    if "vless://" in link:
        return "security=reality" in link or "pbk=" in link
    return True

def check_tcp(link: str, timeout: float = TCP_TIMEOUT) -> bool:
    try:
        normalized = link.replace('hy2://', 'https://').replace('vless://', 'https://')
        parsed = urlparse(normalized)
        host = parsed.hostname
        port = parsed.port
        if not host or not port: return False
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def fetch_links_from_channel(url: str) -> list:
    try:
        target = url.replace('t.me/', 't.me/s/') if 't.me' in url else url
        response = requests.get(target, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200: return []
        pattern = r'(hy2://[^\s<"\'\]\#]+|vless://[^\s<"\'\]\#]+)'
        return re.findall(pattern, response.text)
    except:
        return []

def run():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Файл {SOURCE_FILE} не найден.")
        return
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        sources = json.load(f)
    
    print(f"📡 Обрабатываю {len(sources)} каналов...")
    raw_results = []
    for url in sources:
        links = fetch_links_from_channel(url)
        raw_results.extend([ln for ln in links if is_reality(ln)])

    unique_raw = list(set(raw_results))
    print(f"🧬 Найдено {len(unique_raw)} уникальных ссылок. TCP-проверка...")

    final_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_link = {executor.submit(check_tcp, link): link for link in unique_raw}
        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            if future.result():
                final_list.append(link)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_list))
    print(f"🎉 Готово! {len(final_list)} живых конфигов записаны.")

if __name__ == '__main__':
    run()
