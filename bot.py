import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.payments import GetStarGifts

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

logging.basicConfig(level=logging.INFO)

# --- Keyboards ---
language_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Русский 🇷🇺"), KeyboardButton(text="English 🇬🇧")]],
    resize_keyboard=True
)

intervals_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="10 секунд🕕")],
        [KeyboardButton(text="5 минут🕕")],
        [KeyboardButton(text="1 час🕕")],
        [KeyboardButton(text="1 день🕕")]
    ],
    resize_keyboard=True
)

intervals_en = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="10 seconds🕕")],
        [KeyboardButton(text="5 minutes🕕")],
        [KeyboardButton(text="1 hour🕕")],
        [KeyboardButton(text="1 day🕕")]
    ],
    resize_keyboard=True
)

interval_values = {
    "10 секунд🕕": 10,
    "5 минут🕕": 300,
    "1 час🕕": 3600,
    "1 день🕕": 86400,
    "10 seconds🕕": 10,
    "5 minutes🕕": 300,
    "1 hour🕕": 3600,
    "1 day🕕": 86400
}

# --- In-memory storage ---
user_languages = {}
user_intervals = {}
sent_gift_ids = set()

# --- Handlers ---
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Выбери язык / Choose language:", reply_markup=language_keyboard)

@dp.message(F.text.in_(["Русский 🇷🇺", "English 🇬🇧"]))
async def language_handler(message: types.Message):
    user_id = message.from_user.id
    if message.text == "Русский 🇷🇺":
        user_languages[user_id] = "ru"
        await message.answer("Язык установлен: русский 🇷🇺\n\nВыбери время проверки 🕕", reply_markup=intervals_ru)
    else:
        user_languages[user_id] = "en"
        await message.answer("Language set: English 🇬🇧\n\nChoose check interval 🕕", reply_markup=intervals_en)

@dp.message(F.text.in_(interval_values.keys()))
async def interval_handler(message: types.Message):
    user_id = message.from_user.id
    interval = interval_values[message.text]
    user_intervals[user_id] = interval

    lang = user_languages.get(user_id, "en")
    interval_text = message.text.split()[0]
    response = f"✅ Проверка каждые {interval_text} ✅" if lang == "ru" else f"✅ Check every {interval_text} ✅"
    await message.answer(response)

# --- Background gift checker ---
async def check_gifts():
    await client.start()
    while True:
        try:
            gifts = await client(GetStarGifts())
            for gift in gifts.gifts:
                if gift.id not in sent_gift_ids:
                    sent_gift_ids.add(gift.id)
                    for user_id in user_intervals:
                        lang = user_languages.get(user_id, "en")
                        msg = (
                            f"❗️НОВЫЙ ПОДАРОК ❗️\n{gift.title.text}\nЦена: {gift.star_count}⭐️\n"
                            f"Всего: {gift.total_count}\nОсталось: {gift.remaining_count}"
                            if lang == "ru" else
                            f"❗️NEW GIFT ❗️\n{gift.title.text}\nPrice: {gift.star_count}⭐️\n"
                            f"Total: {gift.total_count}\nLeft: {gift.remaining_count}"
                        )
                        if gift.unique:
                            msg += "\nУникальный ✅" if lang == "ru" else "\nUnique ✅"
                        await bot.send_message(user_id, msg)
        except Exception as e:
            logging.error(f"[ERROR] {e}")
        await asyncio.sleep(5)

# --- Main ---
async def main():
    asyncio.create_task(check_gifts())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
