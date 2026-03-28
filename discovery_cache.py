import json, os, requests, re

def discover():
    file_path = 'telegram_channels.json'
    
    # 1. Загружаем текущую базу (наши 1124+ строк)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                channels = json.load(f)
                if not isinstance(channels, list): channels = []
            except: channels = []
    else:
        channels = []

    print(f"🔎 Исходная база: {len(channels)} каналов")

    # 2. Цели для поиска новых каналов
    search_targets = [
        "https://raw.githubusercontent.com/Catsss3/web-assets-static/main/sources/telegram_channels.json",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/channels",
        "https://raw.githubusercontent.com/v2ray-worker/v2ray-worker/main/sub/sub_merge.txt"
    ]

    new_found = 0
    # Превращаем в set для моментальной проверки на дубликаты
    channels_set = set(channels)
    
    for url in search_targets:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                # Ищем всё, что похоже на ссылки t.me/название
                found = re.findall(r't\.me/[a-zA-Z0-9_+]{3,}', res.text)
                for item in found:
                    full_link = "https://" + item
                    if full_link not in channels_set:
                        channels_set.add(full_link)
                        new_found += 1
        except: continue

    # 3. Сохраняем результат, сортируем для красоты
    final_list = sorted(list(channels_set))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Поиск завершен! Добавлено новых: {new_found}")
    print(f"📊 Итого в базе: {len(final_list)} каналов")

if __name__ == '__main__':
    discover()