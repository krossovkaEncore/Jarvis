import subprocess
import time
import os
import sys
from datetime import datetime

# Цвета вывода (ANSI)
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

LOG_DIR = "bin"
os.makedirs(LOG_DIR, exist_ok=True)

# ⚙️ Список ботов
BOTS = {
    "botJarvisTg.py": "JarvisTg.txt",
    "botJarvisDs.py": "JarvisDs.txt",
    "botSupportTg.py": "SupportTg.txt",
}

def start_bot(bot_name: str):
    """Запускает бота и возвращает процесс"""
    log_path = os.path.join(LOG_DIR, BOTS[bot_name])
    log = open(log_path, "a", encoding="utf-8")
    log.write(f"\n[{datetime.now()}] 🚀 Запуск {bot_name}\n")
    log.flush()
    p = subprocess.Popen(
        [sys.executable, bot_name],
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True
    )
    return p, log, time.time()

print(f"{YELLOW}🔧 Запуск ботов...{RESET}\n")
procs = {}

# Запускаем всех
for bot in BOTS:
    p, log, t = start_bot(bot)
    procs[bot] = {"p": p, "log": log, "start": t}
    print(f"{GREEN}✅ {bot}{RESET} запущен. Логи → {LOG_DIR}/{BOTS[bot]}")
print(f"\nВсе боты запущены. Нажми Ctrl+C для остановки.\n")

try:
    while True:
        time.sleep(2)
        for bot, data in list(procs.items()):
            p = data["p"]
            code = p.poll()
            if code is not None:  # бот завершился
                runtime = time.time() - data["start"]
                log = data["log"]

                log.write(f"[{datetime.now()}] ⚠️ Завершён (код {code}, {runtime:.1f}s)\n")
                log.flush()
                log.close()

                if code == 0:
                    print(f"{YELLOW}ℹ️ {bot}{RESET} завершился нормально (код 0).")
                    del procs[bot]
                    continue

                print(f"{RED}⚠️ {bot} упал (код {code}), перезапуск...{RESET}")
                new_p, new_log, new_t = start_bot(bot)
                procs[bot] = {"p": new_p, "log": new_log, "start": new_t}

except KeyboardInterrupt:
    print(f"\n{YELLOW}🛑 Завершаю всех ботов...{RESET}")
    for bot, data in procs.items():
        data["p"].terminate()
        data["log"].write(f"[{datetime.now()}] 🛑 Остановлено вручную.\n")
        data["log"].close()
    print(f"{GREEN}✅ Все процессы остановлены.{RESET}")
