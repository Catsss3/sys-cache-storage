import os, re, requests

def run():
    # Твои основные источники + новый ShadowProxy66
    channels = ["ShadowProxy66", "v2ray_free-v2ray", "v2ray_free_conf", "V2ray_Alpha"]
    
    results = []
    print(f"📡 Стелла выходит на охоту за свежим мясом...")

    for channel in channels:
        try:
            url = f"https://t.me/s/{channel}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                # Ищем Hy2, Vless и Reality (самые ходовые)
                # Регулярка теперь более гибкая, чтобы мусор не лип
                found = re.findall(r'(hy2://[^\s<"\'\]]+|vless://[^\s<"\'\]]+|reality://[^\s<"\'\]]+)', r.text)
                if found:
                    results.extend(found)
                    print(f"✅ Канал @{channel}: Выжато {len(found)} конфигов!")
        except Exception as e:
            print(f"⚠️ Ошибка на @{channel}: {e}")

    unique = sorted(list(set(results)))
    
    if unique:
        with open("live_configs.txt", "w", encoding='utf-8') as f:
            f.write("\n".join(unique))
        print(f"🎉 Итог: Собрано {len(unique)} уникальных ссылок!")
    else:
        print("💀 Сегодня админы жадничают. Пусто.")

if __name__ == '__main__': run()
