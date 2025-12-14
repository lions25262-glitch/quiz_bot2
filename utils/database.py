import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import CREDENTIALS_FILE, SPREADSHEET_NAME


def connect_sheet():
    """Ulanish Google Sheets ga"""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME).sheet1

        # Ожидаемые столбцы, которые заполняет бот
        expected_headers = ["№", "ID", "Ism", "Familiya", "Maktab", "Sinf", "Telefon", "Vaqt"]

        first_row = sheet.row_values(1)
        if not first_row:
            # Если таблица пустая — создаём заголовки бота
            sheet.insert_row(expected_headers, 1)

        return sheet
    except Exception as e:
        print(f"❌ Google Sheets ulanishda xatolik: {e}")
        return None


def is_registered(user_id):
    """Tekshiradi: foydalanuvchi allaqachon ro'yxatdan o'tganmi"""
    sheet = connect_sheet()
    if not sheet:
        return False
    try:
        ids = sheet.col_values(2)  # ID ustuni
        return str(user_id) in ids
    except Exception as e:
        print(f"⚠ ID tekshirishda xatolik: {e}")
        return False


def save_to_sheet(user):
    """Foydalanuvchi ma'lumotlarini saqlash"""
    sheet = connect_sheet()
    if not sheet:
        return False

    try:
        # Мы читаем только первые 8 столбцов, даже если справа есть дополнительные
        expected_headers = ["№", "ID", "Ism", "Familiya", "Maktab", "Sinf", "Telefon", "Vaqt"]
        all_records = sheet.get_all_records(expected_headers=expected_headers)
        no = len(all_records) + 1
        vaqt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = [
            no,
            user["id"],
            user["ism"],
            user["familiya"],
            user["maktab"],
            user["sinf"],
            user["telefon"],
            vaqt,
        ]

        # Добавляем только нужные поля (лишние колонки не затрагиваются)
        sheet.append_row(data, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        print(f"❌ Saqlashda xatolik: {e}")
        return False
