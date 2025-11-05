import telebot
import config
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

bot = telebot.TeleBot(config.tSupportTg)

user_message_map = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Я — бот для связи с Ильёй.\n"
        f"Напиши сюда свой вопрос — я передам его Илье, и он ответит прямо сюда 🙂"
    )

@bot.message_handler(func=lambda message: message.chat.id != config.admin_id)
def forward_to_admin(message):
    sent = bot.forward_message(config.admin_id, message.chat.id, message.message_id)
    user_message_map[sent.message_id] = message.chat.id

@bot.message_handler(func=lambda message: message.chat.id == config.admin_id and message.reply_to_message)
def admin_reply(message):
    reply_to = message.reply_to_message.message_id
    if reply_to in user_message_map:
        user_id = user_message_map[reply_to]
        bot.send_message(user_id, f"✉️ Ответ от Ильи:\n\n{message.text}")
    else:
        bot.send_message(config.admin_id, "⚠️ Не удалось определить, кому отправить ответ.")

if __name__ == "__main__":
    print("✅ Бот запущен...")
    bot.infinity_polling()
