from Jarvis import jarvis
import telebot, config, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

bot = telebot.TeleBot(config.tJarvisTg)
chat_history = {}



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
    bot.send_message(message.chat.id, jarvis(message.chat.id, message.text, chat_history))
if __name__ == "__main__":
    print("✅ Бот запущен...")
    bot.infinity_polling()
