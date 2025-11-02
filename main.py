import telebot
from telebot import types
import config
from groq import Groq
import os
import re

#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
client = Groq(api_key="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")
bot = telebot.TeleBot(config.token)

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

def jarvis(message):
    resp = client.chat.completions.create(
    messages=[{"role": "user", "content": f"правила/промт:\n{config.promt}\nСообщение владельца: {message.text}"}],model="llama-3.3-70b-versatile")
    return resp.choices[0].message.content

@bot.message_handler(commands=['start'])
def start(message):
    userInWhiteList(message.chat.id)
    bot.send_message(message.chat.id, jarvis(message))

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    userInWhiteList(message.chat.id)
    jarvisOutput = jarvis(message)
    bot.send_message(message.chat.id, jarvisOutput)
    run_console_commands(message.chat.id, jarvisOutput)

if __name__ == "__main__":
    print("✅ Бот запущен...")
    bot.infinity_polling()
