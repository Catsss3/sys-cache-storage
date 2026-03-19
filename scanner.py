import os
import re
import json
import socket
import requests
import concurrent.futures
from urllib.parse import urlparse

# -------------------------------------------------
# Константы
# -------------------------------------------------
SOURCE_FILE = "telegram_channels.json"
OUTPUT_FILE = "live_configs.txt"
MAX_WORKERS = 100       # Оставляем 100, Стелла любит скорость
TCP_TIMEOUT = 2.0       # Оптимально для быстрой отбраковки
REQUEST_TIMEOUT = 10    # Для тяжелых страниц ТГ
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# -------------------------------------------------
# Вспомогательные функции
# -------------------------------------------------

def is_valid_config(link: str) -> bool:
    """
    Проверка на минимальную валидность.
    VLESS берем только с Reality параметрами.
    """
    if not link:
        return False
    if link.startswith("vless://"):
        return "security=reality" in link.lower() or "pbk=" in link.lower()
    return True

def check_tcp(link: str, timeout: float = TCP_TIMEOUT) -> bool:
    """
    Проверяет, открыт ли порт на сервере.
    """
    try:
        # Подменяем протокол для корректного парсинга хоста и порта
        norm = re.sub(r'^(hy2|vless|tuic)://', 'https://', link)
        parsed = urlparse(norm)
        host = parsed.hostname
        port = parsed.port
        
        if not host or not port:
            return False

        # Используем контекстный менеджер для автоматического закрытия
        with socket.create_connection((host, port), timeout=timeout) as sock:
            # На всякий случай явно сигнализируем о завершении
            sock.shutdown(socket.SHUT_RDWR)
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
    except Exception:
        return False

def fetch_links_from_channel(url: str) -> list:
    """
    Парсит публичную версию ТГ-канала (/s/).
    """
    try:
        # Переключаемся на веб-превью, если ссылка обычная
        target = url.replace("t.me/", "t.me/s/") if "t.me/" in url and "/s/" not in url else url
        
        response = requests.get(target, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return []

        # Улучшенная регулярка: ищем до первого пробела или спецсимвола, исключая мусор в конце
        pattern = r"(?:hy2|vless|tuic)://[^\s<\"'|]+(?<![.,;!])"
        found = re.findall(pattern, response.text)

        return [ln for ln in found if is_valid_config(ln)]
    except Exception as e:
        # Можно раскомментировать для отладки: print(f"Ошибка парсинга {url}: {e}")
        return []

# -------------------------------------------------
# Основная логика
# -------------------------------------------------

def run():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Ошибка: Файл {SOURCE_FILE} не найден в директории.")
        return

    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            sources = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Ошибка: {SOURCE_FILE} имеет неверный формат JSON.")
        return

    print(f"📡 Стелла на связи. Начинаю сбор из {len(sources)} источников...")
    
    # Используем set для автоматического удаления дубликатов при сборе
    unique_links = set()

    for i, url in enumerate(sources, 1):
        links = fetch_links_from_channel(url)
        if links:
            unique_links.update(links)
        
        # Индикатор прогресса, чтобы Слава не скучал
        if i % 10 == 0 or i == len(sources):
            print(f"   [Прогресс: {i}/{len(sources)}] Собрано уникальных: {len(unique_links)}")

    if not unique_links:
        print("📭 Ссылок не найдено. Возможно, источники пусты.")
        return

    print(f"🧬 Запускаю TCP‑проверку в {MAX_WORKERS} потоков...")

    final_results = []
    # Используем ThreadPoolExecutor для параллельной проверки портов
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_link = {executor.submit(check_tcp, link): link for link in unique_links}
        
        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            try:
                if future.result():
                    final_results.append(link)
            except Exception:
                pass

    # Сохраняем результат в файл
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_results))

    print("-" * 30)
    print(f"💎 Финал: {len(final_results)} рабочих конфигов сохранены в {OUTPUT_FILE}")
    print(f"📊 Эффективность: {round(len(final_results)/len(unique_links)*100, 1)}% от найденных.")

if __name__ == "__main__":
    run()
