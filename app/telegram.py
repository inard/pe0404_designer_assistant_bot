import os
import telebot
from dotenv import load_dotenv
from assistant import Assistant

load_dotenv()

# Инициализация бота и ассистента
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
assistant = Assistant()

# Словарь для хранения thread_id для каждого пользователя Telegram
user_threads = {}

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    # Устанавливаем источник обращения как "Телеграм"
    assistant.set_source("Телеграм")
    bot.send_message(message.chat.id, "Привет! Я виртуальный помощник веб-дизайнера Екатерины. Чем могу помочь?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработчик всех текстовых сообщений"""
    user_id = message.from_user.id
    user_message = message.text

    # Получаем или создаём thread_id для пользователя
    thread_id = user_threads.get(user_id)
    if not thread_id:
        thread_id = assistant.create_thread()
        user_threads[user_id] = thread_id

    # Устанавливаем источник обращения как "Телеграм"
    assistant.set_source("Телеграм")
    
    # Обрабатываем сообщение через ассистента
    bot_message = assistant.process_message(thread_id, user_message)

    # Отправляем ответ пользователю
    bot.send_message(message.chat.id, bot_message)

def set_webhook(url):
    """Устанавливает webhook URL"""
    bot.set_webhook(url=url)
    print(f"Webhook установлен на: {url}")

def remove_webhook():
    """Убирает webhook"""
    bot.remove_webhook()
    print("Webhook убран")

def process_webhook_update(update_data):
    """Обрабатывает обновление от webhook"""
    update = telebot.types.Update.de_json(update_data)
    bot.process_new_updates([update])

if __name__ == "__main__":
    # Для тестирования можно оставить polling
    print("Telegram bot started with polling...")
    bot.polling(none_stop=True)
