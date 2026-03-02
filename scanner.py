import os, re, requests, json

def run():
    if not os.path.exists("telegram_channels.json"): return
    with open("telegram_channels.json", "r") as f: sources = json.load(f)
    
    results = []
    print(f"📡 Сканирую {len(sources)} каналов...")
    
    for url in sources:
        try:
            # Превращаем в формат предпросмотра, если это ТГ
            target = url.replace('t.me/', 't.me/s/') if 't.me' in url else url
            r = requests.get(target, timeout=10)
            if r.status_code == 200:
                # Ищем Hy2 (без лишних проверок)
                found = re.findall(r'hy2://[^\s,"\'\]<>]+', r.text)
                if found:
                    results.extend(found)
                    print(f"✅ +{len(found)} с {url}")
        except: continue

    unique = list(set(results))
    with open("live_configs.txt", "w") as f: f.write("\n".join(unique))
    print(f"🎉 Итог: Найдено {len(unique)} Hy2.")

if __name__ == '__main__': run()
