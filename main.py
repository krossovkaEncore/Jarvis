import subprocess
import time
import os
from datetime import datetime
LOG_DIR = "bin"
os.makedirs(LOG_DIR, exist_ok=True)
bots = {
    "botJarvisTg.py": "JarvisTg.txt",
    "botJarvisDs.py": "JarvisDs.txt",
    "botSupportTg.py": "SupportTg.txt"
}
processes = {}
def start_bot(bot_file, log_file):
    """Запуск бота и запись лога"""
    log_path = os.path.join(LOG_DIR, log_file)
    log = open(log_path, "a", encoding="utf-8")
    log.write(f"\n[{datetime.now()}] 🚀 Запуск {bot_file}\n")
    log.flush()

    process = subprocess.Popen(
        ["python", bot_file],
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True
    )
    return process, log
try:
    for bot_file, log_file in bots.items():
        p, log = start_bot(bot_file, log_file)
        processes[bot_file] = (p, log)
        print(f"✅ {bot_file} запущен. Логи → {LOG_DIR}/{log_file}")
        time.sleep(1)

    print("\nВсе боты запущены. Нажми Ctrl+C для остановки.\n")
    while True:
        for bot_file, (process, log) in list(processes.items()):
            if process.poll() is not None:
                code = process.returncode
                log.write(f"[{datetime.now()}] ⚠️ {bot_file} остановился (код {code}). Перезапуск...\n")
                log.flush()
                print(f"⚠️ {bot_file} упал (код {code}), перезапускаю...")
                log.close()
                p, new_log = start_bot(bot_file, bots[bot_file])
                processes[bot_file] = (p, new_log)
                time.sleep(2)
        time.sleep(3)

except KeyboardInterrupt:
    print("\n🛑 Завершение работы. Останавливаю все процессы...")
    for bot_file, (process, log) in processes.items():
        process.terminate()
        log.write(f"[{datetime.now()}] 🛑 Завершено вручную.\n")
        log.close()
    print("✅ Все боты остановлены.")
