# -*- coding: utf-8 -*-
import os
import re
import time
import pygame
from TTS.api import TTS
from pathlib import Path
from groq import Groq
import config

# === ИНИЦИАЛИЗАЦИЯ (один раз) ===
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
pygame.mixer.init()

# === ГОВОРИТ ГОЛОСОМ ===
def say(text: str, speaker_wav: str = "paul.wav", language: str = "ru", output_dir: str = "bin"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "output.mp3"
    tts.tts_to_file(
         text=text,
        speaker_wav=speaker_wav,
        language=language,
        file_path=str(output_path)
    )
    start_time = time.time()
    while not output_path.exists():
        if time.time() - start_time > 20:
            return
        time.sleep(0.1)
    pygame.mixer.music.load(str(output_path))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    if output_path.exists():
        output_path.unlink()

# === ОСНОВНАЯ ФУНКЦИЯ ===
def jarvis(chat_id, message):
    # Запрос к Groq
    client = Groq(api_key=config.tokenGroq)
    response = client.chat.completions.create(
        model=config.aiModel,
        messages=[
            {"role": "system", "content": config.prompt},
            {"role": "user", "content": message}
        ]
    )
    answer = response.choices[0].message.content

    # Выполняем команды
    cmd = re.search(r'console:\{([^}]*)\}', answer)
    if cmd:
        os.system(cmd.group(1))
        answer += f"\n\nВыполнено: {cmd.group(1)}"

    # Говорим вслух (если не local)
    if chat_id == 'local':
        say(answer)

    return answer

# === ТЕСТ ===
if __name__ == "__main__":
    while True:
        msg = input("Ты: ")
        if msg in ["выход", "exit"]: break
        print("JARVIS:", jarvis(776247660, msg))