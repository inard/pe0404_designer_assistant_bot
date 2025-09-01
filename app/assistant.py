import os
import time
import json
import openai
from dotenv import load_dotenv
from googlesheets import GoogleSheetsManager
from notifier import TelegramNotifier

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')

# Создаем один экземпляр GoogleSheetsManager для всех экземпляров Assistant
_shared_sheets_manager = GoogleSheetsManager()

# Создаем один экземпляр TelegramNotifier для всех экземпляров Assistant
_shared_notifier = TelegramNotifier()

class Assistant:
    def __init__(self):
        self.assistant_id = OPENAI_ASSISTANT_ID
        # Используем общий экземпляр GoogleSheetsManager
        self.sheets_manager = _shared_sheets_manager
        # Используем общий экземпляр TelegramNotifier
        self.notifier = _shared_notifier
        self.current_source = "Неизвестно"  # Источник текущего запроса
    
    def set_source(self, source):
        """Устанавливает источник обращения для текущего запроса"""
        self.current_source = source
    
    def create_thread(self):
        """Создаёт новый thread для пользователя"""
        thread = openai.beta.threads.create()
        return thread.id
    
    def add_user_message(self, thread_id, message):
        """Добавляет сообщение пользователя в thread"""
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
    
    def run_assistant(self, thread_id):
        """Запускает ассистента, обрабатывает function calling и ждёт завершения"""
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )

        # Пуллим статус и при необходимости обрабатываем tools
        for _ in range(60):  # максимум ~60 секунд ожидания
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            if run_status.status == "completed":
                return True

            if run_status.status == "requires_action":
                tool_outputs = []
                for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.type == "function" and tool_call.function.name == "save_client_request":
                        # Парсим аргументы и сохраняем
                        try:
                            args = json.loads(tool_call.function.arguments or "{}")
                        except Exception as e:
                            args = {"_raw": tool_call.function.arguments}
                            print(f"Ошибка парсинга аргументов: {e}")

                        # Сохранение в Google Sheets
                        saved = self.sheets_manager.save_client_request(args, self.current_source)
                        # Уведомление в Telegram группу
                        notified = self.notifier.send_client_request(args, self.current_source)

                        # Возвращаем успех только если хотя бы одно действие прошло успешно
                        success = bool(saved or notified)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"success": "true" if success else "false"})
                        })
                    else:
                        # Неизвестный инструмент — отвечаем нейтрально
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"success": "false", "error": "unknown_tool"})
                        })

                # Отправляем результаты инструментов
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run_status.status == "failed":
                return False

            time.sleep(1)

        return False  # время ожидания истекло
    
    def get_assistant_response(self, thread_id):
        """Получает ответ ассистента из thread"""
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        
        # Находим последнее сообщение ассистента
        bot_message = None
        for msg in messages.data:
            if msg.role == "assistant":
                bot_message = msg.content[0].text.value
                break
        
        return bot_message or "[Нет ответа от ассистента]"
    
    def process_message(self, thread_id, user_message):
        """Обрабатывает сообщение пользователя и возвращает ответ ассистента"""
        # Добавляем сообщение пользователя
        self.add_user_message(thread_id, user_message)
        
        # Запускаем ассистента
        if not self.run_assistant(thread_id):
            return "Ошибка выполнения ассистента"
        
        # Получаем ответ
        return self.get_assistant_response(thread_id)
