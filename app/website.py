from flask import Blueprint, render_template, request, jsonify, session
from assistant import Assistant

website_bp = Blueprint('website', __name__)
assistant = Assistant()

# Храним историю чата в памяти (до 30 сообщений)
chat_history = []
MAX_HISTORY = 30

@website_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html', chat_history=chat_history)

@website_bp.route('/send', methods=['POST'])
def send():
    user_message = request.form.get('message')
    if not user_message:
        return jsonify({'error': 'Пустое сообщение'}), 400

    # Получаем или создаём thread_id для пользователя
    thread_id = session.get('thread_id')
    if not thread_id:
        thread_id = assistant.create_thread()
        session['thread_id'] = thread_id

    # Устанавливаем источник обращения как "Сайт"
    assistant.set_source("Сайт")
    
    # Обрабатываем сообщение через ассистента
    bot_message = assistant.process_message(thread_id, user_message)

    # Добавляем в историю (локально, для отображения)
    chat_history.append({'role': 'user', 'content': user_message})
    chat_history.append({'role': 'assistant', 'content': bot_message})
    if len(chat_history) > MAX_HISTORY:
        chat_history.pop(0)
        chat_history.pop(0)

    return jsonify({'reply': bot_message})
