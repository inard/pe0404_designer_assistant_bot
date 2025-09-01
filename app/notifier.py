import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')

class TelegramNotifier:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_GROUP_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    def is_configured(self) -> bool:
        return bool(self.base_url and self.chat_id)

    def send_client_request(self, data: dict, source: str) -> bool:
        if not self.is_configured():
            print("Telegram notifier is not configured: missing TELEGRAM_BOT_TOKEN or TELEGRAM_GROUP_ID")
            return False

        name = data.get('name', '')
        phone = data.get('phone', '')
        dt = data.get('datetime', '')
        comment = data.get('comment', '')

        text = (
            "🆕 Новая заявка на консультацию\n"
            f"📣 Источник: {source}\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"🗓️ Дата и время: {dt}\n"
            f"💬 Комментарий: {comment}"
        )

        try:
            resp = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "disable_web_page_preview": True
                },
                timeout=10
            )
            return resp.ok
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")
            return False
