import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile
import os
import pygame
import logging
from faster_whisper import WhisperModel
from Jarvis import jarvis

# === НАСТРОЙКИ ===
SR = 16000
CHUNK_SEC = 0.25
CHUNK = int(SR * CHUNK_SEC)
SILENCE_TIMEOUT = 0.7  # чуть больше, чтобы не обрывать фразу
RMS_THRESHOLD = 0.015  # подбери под свой микрофон
WAKE_WORDS = ["джарвис", "jarvis", "жарвис", "джарви", "jarvis", "жарви", "Джаррус"]

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JarvisVoice")

# === МОДЕЛЬ ===
print("Загрузка модели faster-whisper...")
model = WhisperModel("small", device="cpu", compute_type="int8")  # small — баланс скорости/качества
# tiny — быстрее, но хуже; base — средне; small — хорошо для ru
pygame.mixer.init()

def rms(data: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(data))))

def save_wav(data: np.ndarray, rate: int, path: str):
    int_data = np.int16(data / np.max(np.abs(data)) * 32767) if np.max(np.abs(data)) > 0 else data
    wavfile.write(path, rate, int_data.astype(np.int16))

def transcribe(wav_path: str) -> str:
    try:
        segments, info = model.transcribe(
            wav_path,
            beam_size=5,
            language="ru",
            vad_filter=True,           # Убирает тишину
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        text = " ".join(seg.text for seg in segments).strip()
        confidence = info.language_probability if hasattr(info, 'language_probability') else 0
        logger.info(f"Распознано: '{text}' (уверенность: {confidence:.2f})")
        return text.lower()
    except Exception as e:
        logger.error(f"Ошибка распознавания: {e}")
        return ""

# === ГОЛОСОВОЙ ЦИКЛ ===
recording = False
frames = []
silence_counter = 0.0

print("Джарвис слушает... (скажи 'Джарвис')")

with sd.InputStream(channels=1, samplerate=SR, blocksize=CHUNK, dtype='float32') as stream:
    while True:
        try:
            block, _ = stream.read(CHUNK)
        except Exception as e:
            logger.error(f"Ошибка чтения аудио: {e}")
            continue

        mono = block.flatten()
        level = rms(mono)

        if level > RMS_THRESHOLD:
            if not recording:
                logger.info("Начинаю запись...")
                recording = True
                frames = []
                silence_counter = 0.0
            frames.append(mono.copy())
            silence_counter = 0.0
        else:
            if recording:
                silence_counter += CHUNK_SEC
                if silence_counter >= SILENCE_TIMEOUT:
                    if frames:
                        audio = np.concatenate(frames)
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                            wav_path = f.name
                        save_wav(audio, SR, wav_path)

                        text = transcribe(wav_path)

                        if any(word in text for word in WAKE_WORDS):
                            logger.info(f"АКТИВАЦИЯ: {text}")
                            try:
                                jarvis('local', text)
                            except Exception as e:
                                logger.error(f"Ошибка в jarvis(): {e}")

                        try:
                            os.unlink(wav_path)
                        except:
                            pass

                    recording = False
                    frames = []
                    silence_counter = 0.0