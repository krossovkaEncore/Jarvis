from Jarvis import jarvis
import telebot
import config
import os
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

bot = telebot.TeleBot(config.tJarvisTg)
chat_history = {}

def run_console_commands(chat_id, text):
    commands = re.findall(r'console:\{([^}]*)\}', text)
    for cmd in commands:
        cmd = cmd.strip()
        bot.send_message(chat_id, f"Выполняю: {cmd}")
        if any(cmd.lower().startswith(sc) for sc in config.SAFE_COMMANDS):
            os.system(cmd)
        else:
            bot.send_message(chat_id, f"⚠️ Команда '{cmd}' не в списке разрешённых.")

def userInWhiteList(chat_id):
        if not(chat_id in config.whiteList):
            bot.send_message(chat_id, "Нет прав, уж извени😢")
            pass

@bot.message_handler(commands=['start'])
def start(message):
    userInWhiteList(message.chat.id)
    bot.send_message(message.chat.id, jarvis(message.chat.id, 'привет'))

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    userInWhiteList(message.chat.id)
    jarvisOutput = jarvis(message.chat.id, message.text, chat_history)
    bot.send_message(message.chat.id, jarvisOutput)
    run_console_commands(message.chat.id, jarvisOutput)

if __name__ == "__main__":
    print("✅ Бот запущен...")
    bot.infinity_polling()
