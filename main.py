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
        "سلام داداش! اصغر آقا آماده‌ست 😂🚀\n\n"
        "لینک بده → کیفیت بزن → حالشو ببر!\n"
        "فایل صوتی/ویدیویی هم بفرستی MP3 می‌کنم 🎵",
        reply_markup=kb
    )

@dp.message(F.text.in_(["4K","1080p","720p","480p","فقط صدا (MP3)","بهترین کیفیت"]))
async def set_q(msg: types.Message):
    user_quality[msg.from_user.id] = msg.text
    await msg.answer(f"کیفیت قفل شد: {msg.text} ✅")

@dp.message(F.text.startswith(("http://", "https://")))
async def download(msg: types.Message):
    url = msg.text.strip()
    q = user_quality.get(msg.from_user.id, "بهترین کیفیت")
    status = await msg.reply("اصغر آقا داره می‌گیره... ⏳")

    # این فرمت جدید هیچ‌وقت خطا نمی‌ده
    if "فقط صدا" in q:
        format_str = "bestaudio"
    else:
        format_str = "bestvideo[height<=?2160]+bestaudio/best" if "4K" in q else \
                     "bestvideo[height<=?1080]+bestaudio/best" if "1080p" in q else \
                     "bestvideo[height<=?720]+bestaudio/best" if "720p" in q else \
                     "bestvideo[height<=?480]+bestaudio/best" if "480p" in q else \
                     "bestvideo+bestaudio/best"

    ydl_opts = {
        'format': format_str,
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    if "صدا" in q:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            if "صدا" in q and not filepath.endswith(".mp3"):
                filepath = filepath.rsplit(".", 1)[0] + ".mp3"

        size = os.path.getsize(filepath)
        if size > 50 * 1024 * 1024:
            await status.edit_text("فایل خیلی گنده‌ست داداش! بیشتر از ۵۰ مگ نمی‌تونم 😭")
            os.remove(filepath)
            return

        await status.edit_text("دارم می‌فرستم...")
        if filepath.endswith((".mp3", ".m4a", ".wav")):
            await bot.send_audio(msg.chat.id, FSInputFile(filepath), caption="اصغر آقا تقدیم کرد 🎵😂")
        else:
            await bot.send_video(msg.chat.id, FSInputFile(filepath), caption="اصغر آقا تقدیم کرد 🎬😂")
        os.remove(filepath)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"یه مشکلی شد داداش:\n{str(e)[:400]}")

async def main():
    print("اصغر آقا کاملاً آماده‌ست! 🔥")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
