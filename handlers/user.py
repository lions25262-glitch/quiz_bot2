from telebot import types
from datetime import datetime
from utils.database import save_to_sheet, is_registered

user_data = {}

maktablar = [
    "1-maktab", "2-maktab", "3-maktab", "4-maktab", "5-maktab", "6-maktab",
    "7-maktab", "8-maktab", "9-maktab", "10-maktab", "11-maktab", "12-maktab",
    "13-maktab", "14-maktab", "15-maktab", "16-maktab", "17-maktab", "18-maktab",
    "19-maktab", "20-maktab", "21-maktab", "22-maktab", "23-maktab", "24-maktab",
    "25-maktab", "26-maktab", "27-maktab", "28-maktab", "29-maktab", "30-maktab",
    "31-maktab", "32-maktab", "33-maktab", "34-maktab", "35-maktab", "36-maktab",
    "37-maktab", "38-maktab", "39-maktab", "40-maktab", "41-maktab", "42-maktab",
]



CHANNEL_USERNAME = "@xojeli_imperial_school"

def check_subscription(bot, user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except Exception:
        print(1)
        return False

def register_handlers(bot):
    # Выбор предмета
    @bot.callback_query_handler(func=lambda call: call.data == "register")
    def start_registration(call):
        user_id = call.from_user.id

        if is_registered(user_id):
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "✅ Siz allaqachon ro‘yxatdan o‘tgan ekansiz!")
            return

        # Проверяем подписку
        if not check_subscription(bot, user_id):
            bot.answer_callback_query(call.id)

            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("📢 Kanalga o‘tish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"),
                types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscribe")
            )
            bot.send_message(
                call.message.chat.id,
                "❗ Ro‘yxatdan o‘tish uchun avval kanalga obuna bo‘ling.",
                reply_markup=markup
            )
            return

        # Если подписан — начинаем регистрацию
        user_data[user_id] = {}
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Ismingizni kiriting:")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, ism_qabul, user_id)
    # Имя
    def ism_qabul(msg, user_id):
        user_data[user_id]["ism"] = msg.text.strip()
        msg = bot.send_message(msg.chat.id, "Familiyangizni kiriting:")
        bot.register_next_step_handler(msg, familiya_qabul, user_id)

    # Фамилия
    def familiya_qabul(msg, user_id):
        user_data[user_id]["familiya"] = msg.text.strip()

        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for m in maktablar:
            buttons.append(types.InlineKeyboardButton(text=m, callback_data=f"maktab_{m}"))
        # Добавляем по 2 кнопки в ряд
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i+2])

        bot.send_message(msg.chat.id, "🏫 Maktabingizni tanlang:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "check_subscribe")
    def check_subscribe(call):
        user_id = call.from_user.id
        if check_subscription(bot, user_id):
            bot.answer_callback_query(call.id, "✅ Obuna tekshirildi!")
            bot.send_message(call.message.chat.id, "Ismingizni kiriting:")
            user_data[user_id] = {}
            bot.register_next_step_handler_by_chat_id(call.message.chat.id, ism_qabul, user_id)
        else:
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                "🚫 Siz hali ham kanalga obuna bo‘lmagansiz.\nIltimos, avval obuna bo‘ling."
            )

    # Выбор школы
    @bot.callback_query_handler(func=lambda call: call.data.startswith("maktab_"))
    def maktab_tanlash(call):
        user_id = call.from_user.id
        maktab = call.data.replace("maktab_", "")
        user_data[user_id]["maktab"] = maktab
        bot.answer_callback_query(call.id)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{maktab} tanlandi ✅"
        )

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("3-sinf", callback_data="sinf_3"),
            types.InlineKeyboardButton("4-sinf", callback_data="sinf_4")
        )

        bot.send_message(call.message.chat.id, "📚 Sinfingizni tanlang:", reply_markup=markup)

    # Выбор класса
    @bot.callback_query_handler(func=lambda call: call.data.startswith("sinf_"))
    def sinf_tanlash(call):
        user_id = call.from_user.id
        sinf = call.data.replace("sinf_", "")
        user_data[user_id]["sinf"] = sinf
        bot.answer_callback_query(call.id)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{sinf}-sinf tanlandi ✅"
        )

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        phone_btn = types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
        markup.add(phone_btn)

        bot.send_message(
            call.message.chat.id,
            "Iltimos, telefon raqamingizni yuboring:",
            reply_markup=markup
        )

    # Обработка телефона
    @bot.message_handler(content_types=["contact"])
    def contact_handler(msg):
        user_id = msg.from_user.id
        if user_id not in user_data:
            return

        user_data[user_id]["id"] = user_id
        user_data[user_id]["telefon"] = msg.contact.phone_number
        user_data[user_id]["vaqt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        success = save_to_sheet(user_data[user_id])

        if success:
            bot.send_message(
                msg.chat.id,
                "✅ Ma’lumotlaringiz muvaffaqiyatli saqlandi!\n\nRahmat ishtirokingiz uchun! 🎉",
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            bot.send_message(
                msg.chat.id,
                "⚠ Ma’lumotlarni saqlashda xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.",
                reply_markup=types.ReplyKeyboardRemove()
            )

        user_data.pop(user_id, None)
