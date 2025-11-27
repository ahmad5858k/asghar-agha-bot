import os
import asyncio
import yt_dlp
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram import F

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [types.KeyboardButton(text="4K")],
    [types.KeyboardButton(text="1080p")],
    [types.KeyboardButton(text="720p")],
    [types.KeyboardButton(text="480p")],
    [types.KeyboardButton(text="فقط صدا (MP3)")],
    [types.KeyboardButton(text="بهترین کیفیت")]
])

user_quality = {}

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "سلام داداش! اصغر آقا آماده‌ست 😂\n\n"
        "لینک بده → کیفیت بزن → حالشو ببر!\n"
        "فایل هم بفرستی MP3 می‌کنم 🎵",
        reply_markup=kb
    )

@dp.message(F.text.in_(["4K","1080p","720p","480p","فقط صدا (MP3)","بهترین کیفیت"]))
async def set_q(msg: types.Message):
    user_quality[msg.from_user.id] = msg.text
    await msg.answer(f"کیفیت قفل شد: {msg.text} ✅")

@dp.message(F.text.startswith(("http://", "https://")))
async def download(msg: types.Message):
    url = msg.text.strip()
    q = user
