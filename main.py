import os
import asyncio
import yt_dlp
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram import F

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# کیبورد کیفیت
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
        "سلام داداش! اصغر آقا اومد خدمتت 😂🚀\n\n"
        "لینک ویدیو یا آهنگ از هر جا بفرست (یوتیوب، اینستا، تیکتاک، توییتر، اسپاتیفای و...)\n"
        "کیفیت رو انتخاب کن و حالشو ببر!\n\n"
        "فایل صوتی یا ویدیویی هم بفرستی برات MP3 می‌کنم 🎵",
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
    status = await msg.reply("اصغر آقا داره می‌ره دنبالش... ⏳")

    format_str = "best"
    if "4K" in q: format_str = "bestvideo[height<=2160]+bestaudio/best"
    elif "1080p" in q: format_str = "bestvideo[height<=1080]+bestaudio/best"
    elif "720p" in q: format_str = "bestvideo[height<=720]+bestaudio/best"
    elif "480p" in q: format_str = "bestvideo[height<=480]+bestaudio/best"
    if "فقط صدا" in q: format_str = "bestaudio"

    ydl_opts = {
        'format': format_str,
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }
    if "فقط صدا" in q:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            if "فقط صدا" in q and not filepath.endswith(".mp3"):
                filepath = filepath.rsplit(".", 1)[0] + ".mp3"

        await status.edit_text("دارم می‌فرستم... 📤")

        if os.path.getsize(filepath) > 50 * 1024 * 1024:
            await status.edit_text("فایل خیلی گنده‌ست داداش! بیشتر از ۵۰ مگ نمی‌تونم بفرستم 😅")
            os.remove(filepath)
            return

        if filepath.endswith((".mp3", ".m4a")):
            await bot.send_audio(msg.chat.id, FSInputFile(filepath), caption="اصغر آقا تقدیم کرد 🎵😂")
        else:
            await bot.send_video(msg.chat.id, FSInputFile(filepath), caption="اصغر آقا تقدیم کرد 🎬😂")

        os.remove(filepath)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"یه چیزی شد داداش...\nخطا: {str(e)}")

@dp.message(F.document | F.video | F.audio | F.voice)
async def convert(msg: types.Message):
    await msg.reply("صبر کن اصغر آقا داره MP3 می‌کنه... 🎵")
    file_id = (msg.document or msg.video or msg.audio or msg.voice).file_id
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, "/tmp/input.tmp")
    subprocess.run(["ffmpeg", "-i", "/tmp/input.tmp", "-q:a", "0", "-map", "a", "/tmp/output.mp3", "-y"])
    await bot.send_audio(msg.chat.id, FSInputFile("/tmp/output.mp3"), title="اصغر آقا تبدیل کرد 😂")
    os.remove("/tmp/input.tmp")
    os.remove("/tmp/output.mp3")

async def main():
    print("اصغر آقا آنلاین شد! 😂🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
