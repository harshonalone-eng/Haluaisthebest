import os
import logging
import yt_dlp
import imageio_ffmpeg

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8819149020:AAH_qW1JO6a2yQBVB0CrJ0rnuwcHvrfRsQQ"

logging.basicConfig(level=logging.INFO)

# FFmpeg path
os.environ["PATH"] += os.pathsep + os.path.dirname(
    imageio_ffmpeg.get_ffmpeg_exe()
)

def is_youtube_link(text):
    return "youtube.com" in text or "youtu.be" in text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot chalu hai ✅\n\n"
        "YouTube link ke end me .audio lagao.\n\n"
        "Example:\n"
        "https://youtu.be/VIDEO_ID .audio"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Agar .audio nahi hai
    if not text.endswith(".audio"):
        await update.message.reply_text(
            "The response is not authorized"
        )
        return

    # .audio hatao
    url = text.replace(".audio", "").strip()

    # YouTube link check
    if not is_youtube_link(url):
        await update.message.reply_text(
            "The response is not authorized"
        )
        return

    await update.message.reply_text("Audio bana raha hoon...")

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio_%(id)s.%(ext)s",
            "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "noplaylist": True,
            "quiet": True,
        }

        # Download + convert
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            mp3_file = f"audio_{info['id']}.mp3"

        # Send audio
        with open(mp3_file, "rb") as audio:
            await update.message.reply_audio(
                audio=audio,
                title=info.get("title", "Audio")
            )

        # Delete file
        os.remove(mp3_file)

    except Exception as e:
        await update.message.reply_text(
            f"Error:\n{e}"
        )

def main():
    print("BOT START HO RAHA HAI...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("BOT RUNNING ✅")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()