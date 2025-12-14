from telebot import TeleBot, types
from config import BOT_TOKEN
from handlers.user import register_handlers

bot = TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(msg):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 Dizimnen ótiw", callback_data="register"))

    bot.send_photo(
        msg.chat.id,
        photo=open('img.png', 'rb'),
        caption=(
            "🧠 Bul olimpiadanıń maqseti 3–4-klasslar arasında matematika hám ingliz tili páninen "
            "báseki payda etiw, matematika hám ingliz tili pánlerine qızıqtırıw, "
            "balalardıń bos waqtın ónimli hám paydalı ótkeriw bolıp esaplanadı. "
            "Olimpiadada túsken qarjınıń úlken bólegin qatnasıwshılar arasında "
            "joqarı nátiyje kórsetken oqıwshılarǵa sawǵa yamasa pul kórinisinde beriw."
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )

# Подключаем все обработчики
register_handlers(bot)

print("Bot started...")
bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=20, none_stop=True)

