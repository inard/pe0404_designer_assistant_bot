import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

class GoogleSheetsManager:
    def __init__(self):
        self.service_account_path = os.getenv('GOOGLE_SERVICE_ACCOUNT')
        self.sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        self.sheet = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Инициализирует подключение к Google Sheets"""
        if not self.service_account_path or not self.sheets_id:
            print("Google Sheets не настроен: отсутствуют GOOGLE_SERVICE_ACCOUNT или GOOGLE_SHEETS_ID")
            return
        
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(self.service_account_path, scopes=scope)
            gc = gspread.authorize(creds)
            self.sheet = gc.open_by_key(self.sheets_id).sheet1
            print("Google Sheets подключение установлено")
        except Exception as e:
            print(f"Ошибка подключения к Google Sheets: {e}")
            self.sheet = None
    
    def save_client_request(self, data, source="Неизвестно"):
        """Сохраняет заявку клиента в Google Sheets"""
        if not self.sheet:
            print("Google Sheets не инициализирован")
            return False
        
        try:
            # Подготавливаем данные для записи в колонки: Имя, Телефон, Дата и время, Комментарий, Источник обращения
            row_data = [
                data.get('name', ''),
                data.get('phone', ''),
                data.get('datetime', ''),
                data.get('comment', ''),
                source
            ]
            
            # Добавляем новую строку
            self.sheet.append_row(row_data)
            print(f"Данные клиента {data.get('name', 'Unknown')} успешно сохранены в Google Sheets (источник: {source})")
            return True
        except Exception as e:
            print(f"Ошибка сохранения в Google Sheets: {e}")
            return False
    
    def is_available(self):
        """Проверяет доступность Google Sheets"""
        return self.sheet is not None
