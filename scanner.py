import os
import re
import json
import socket
import base64
import requests
import concurrent.futures
from threading import Semaphore
from urllib.parse import urlparse

# -------------------------------------------------
# Константы
# -------------------------------------------------
SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"

MAX_TCP_WORKERS = 100          # Агрессивная проверка портов
MAX_HTTP_WORKERS = 15          # Бережный парсинг источников
TCP_TIMEOUT = 2.0
REQUEST_TIMEOUT = 12

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Используем сессию для ускорения HTTP-запросов
session = requests.Session()
session.headers.update(HEADERS)

# -------------------------------------------------
# Валидация и декодирование
# -------------------------------------------------

def is_valid_config(link: str) -> bool:
    """Только VLESS (Reality) и живые HY2/TUIC."""
    ln = link.lower()
    if ln.startswith("vless://"):
        return "security=reality" in ln or "pbk=" in ln
    return ln.startswith(("hy2://", "tuic://"))

def check_tcp(link: str, timeout: float = TCP_TIMEOUT) -> bool:
    """Проверка доступности хоста и порта."""
    try:
        # Убираем лишние пробелы и готовим для парсинга
        norm = re.sub(r"^(hy2|vless|tuic)://", "https://", link.strip(), flags=re.IGNORECASE)
        parsed = urlparse(norm)
        host, port = parsed.hostname, parsed.port
        if not host or not port:
            return False

        # Попытка установить соединение
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def fetch_links_from_source(url: str) -> list:
    """Универсальный парсер: TG, GitHub, API, Base64."""
    try:
        # Подготовка URL для Telegram
        target = url.replace("t.me/", "t.me/s/") if "t.me/" in url and "/s/" not in url else url
        
        resp = session.get(target, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code != 200:
            return []

        content = resp.text

        # Декодирование Base64 (если в тексте нет явных ссылок)
        if not any(proto in content for proto in ("vless://", "hy2://", "tuic://")):
            try:
                # Очистка и паддинг
                b64_candidate = re.sub(r"\s+", "", content)
                missing = len(b64_candidate) % 4
                if missing:
                    b64_candidate += "=" * (4 - missing)
                
                decoded = base64.b64decode(b64_candidate, validate=False).decode("utf-8", errors="ignore")
                content = decoded
            except:
                pass

        # Поиск ссылок по элитному паттерну (с негативным просмотром назад)
        pattern = r"(?:hy2|vless|tuic)://[^\s<\"'|]+(?<![.,;!])"
        found = re.findall(pattern, content, flags=re.IGNORECASE)

        return [ln for ln in found if is_valid_config(ln)]
    except:
        return []

# -------------------------------------------------
# Основной процесс
# -------------------------------------------------

def run():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Файл {SOURCE_FILE} не найден.")
        return

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        sources = json.load(f)

    print(f"📡 Стелла начинает сбор. Источников: {len(sources)}")
    unique_links = set()
    http_semaphore = Semaphore(MAX_HTTP_WORKERS)

    def safe_fetch(u):
        with http_semaphore:
            return fetch_links_from_source(u)

    # 1. Сбор ссылок
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_HTTP_WORKERS) as pool:
        futures = {pool.submit(safe_fetch, url): url for url in sources}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            links = future.result()
            if links:
                unique_links.update(links)
            if i % 50 == 0:
                print(f"   [Парсинг] {i}/{len(sources)} каналов → {len(unique_links)} уникальных ссылок")

    if not unique_links:
        print("📭 Улов пуст. Проверь источники!")
        return

    # 2. TCP Проверка
    print(f"🧬 Запускаю TCP-чек для {len(unique_links)} ссылок...")
    final_results = []
    checked = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_TCP_WORKERS) as pool:
        future_to_link = {pool.submit(check_tcp, l): l for l in unique_links}
        for future in concurrent.futures.as_completed(future_to_link):
            checked += 1
            if future.result():
                final_results.append(future_to_link[future])
            if checked % 200 == 0 or checked == len(unique_links):
                print(f"   [TCP] Проверено {checked}/{len(unique_links)} → {len(final_results)} живых")

    # 3. Сохранение
    final_results.sort()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_results))

    print("-" * 40)
    print(f"💎 Стелла закончила! Рабочих конфигов: {len(final_results)}")
    print(f"📂 Файл сохранен: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
