
import re, requests, json, os
import google.generativeai as genai

def run():
    # Загружаем базу каналов
    with open("telegram_channels.json", "r") as f:
        channels = json.load(f)
    
    # 1. Gemini ищет новые источники (используем GEMINI_API_KEY)
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Provide 10 public Telegram channel names (only names, like 'v2ray_collector') that share VLESS and Hysteria2. Educational research."
            res = model.generate_content(prompt)
            new_found = re.findall(r'(\w+)', res.text)
            channels = list(set(channels + new_found))
            with open("telegram_channels.json", "w") as f: 
                json.dump(channels, f, indent=2)
    except Exception as e: 
        print(f"Gemini skipped: {e}")

    # 2. Сбор конфигов (VLESS и Hysteria2)
    found_configs = []
    print(f"Scanning {len(channels)} channels...")
    for ch in channels:
        try:
            r = requests.get(f"https://t.me/s/{ch}", timeout=15)
            # Ищем vless и hysteria2
            vless = re.findall(r'vless://[a-zA-Z0-9%@&?#=_.:/-]+', r.text)
            hy2 = re.findall(r'hysteria2://[a-zA-Z0-9%@&?#=_.:/-]+', r.text)
            found_configs.extend(vless + hy2)
        except: continue
    
    # 3. Убираем дубликаты и сохраняем
    unique = list(set(found_configs))
    with open("live_configs.txt", "w") as f:
        f.write("\n".join(unique))
    print(f"Done! Saved {len(unique)} configs.")

if __name__ == "__main__":
    run()
