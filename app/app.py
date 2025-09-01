import os
from flask import Flask, request
from dotenv import load_dotenv
from website import website_bp
from telegram import process_webhook_update

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev')

# Регистрируем Blueprint для веб-интерфейса
app.register_blueprint(website_bp)

# Путь для webhook'а Telegram
telegram_webhook_path = os.getenv('TELEGRAM_WEBHOOK_URL', '/webhook')

@app.route(telegram_webhook_path, methods=['POST'])
def webhook():
    """Webhook для получения обновлений от Telegram"""
    if request.headers.get('content-type') == 'application/json':
        update_data = request.get_json()
        process_webhook_update(update_data)
        return 'OK'
    return 'Bad Request', 400

if __name__ == '__main__':
    app.run(debug=True)
