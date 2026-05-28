import os
import re
import base64
import requests
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8819149020:AAH_qW1JO6a2yQBVB0CrJ0rnuwcHvrfRsQQ"
OPENROUTER_API_KEY = "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"

DEEPSEEK_API = "https://deepseekreasoning.suryahacker.workers.dev/"

def clean_name(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:80]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤖 AI Chat", callback_data="ai"),
         InlineKeyboardButton("🖼 Image", callback_data="image")],
        [InlineKeyboardButton("🎵 Music", callback_data="music"),
         InlineKeyboardButton("🎧 Audio", callback_data="audio")]
    ]

    text = (
        "🔥 MULTI BOT 🔥\n\n"
        ".ai hello\n"
        ".image wolf with red eyes\n"
        ".audio YouTube_Link\n"
        ".music song name"
    )

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    help_text = {
        "ai": "Use:\n.ai hello",
        "image": "Use:\n.image wolf with red eyes",
        "audio": "Use:\n.audio https://youtu.be/videoid",
        "music": "Use:\n.music faded alan walker"
    }

    await q.message.reply_text(help_text.get(q.data, "Use /start"))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower().startswith(".ai"):
        prompt = text[3:].strip()

        if not prompt:
            await update.message.reply_text("Example:\n.ai hello")
            return

        msg = await update.message.reply_text("🤖 Thinking...")

        try:
            r = requests.get(DEEPSEEK_API, params={"query": prompt}, timeout=60)
            data = r.json()

            reply = (
                data.get("result", {}).get("response")
                or data.get("response")
                or str(data)
            )

            await msg.edit_text(reply[:4000])

        except Exception as e:
            await msg.edit_text(f"AI Error:\n{e}")

    elif text.lower().startswith(".image"):
        prompt = text[6:].strip()

        if not prompt:
            await update.message.reply_text("Example:\n.image wolf with red eyes")
            return

        msg = await update.message.reply_text("🖼 Generating image...")

        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "x-ai/grok-imagine-image-quality",
                    "modalities": ["image", "text"],
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                timeout=120
            )

            data = r.json()

            if "error" in data:
                await msg.edit_text(f"Image API Error:\n{data['error']}")
                return

            message = data["choices"][0]["message"]

            image_url = None
            image_base64 = None

            images = message.get("images") or []
            if images:
                image_info = images[0].get("image_url", {})
                image_url = image_info.get("url")

            if not image_url:
                content = message.get("content", "")
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "image_url":
                            image_url = item.get("image_url", {}).get("url")

            if image_url and image_url.startswith("data:image"):
                image_base64 = image_url.split(",", 1)[1]
                file_path = "generated_image.png"

                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(image_base64))

                await update.message.reply_photo(photo=open(file_path, "rb"), caption=prompt)
                os.remove(file_path)

            elif image_url:
                await update.message.reply_photo(photo=image_url, caption=prompt)

            else:
                await msg.edit_text(f"Image response mila, par image URL nahi mila:\n{data}")

            await msg.delete()

        except Exception as e:
            await msg.edit_text(f"Image Error:\n{e}")

    elif text.lower().startswith(".audio"):
        url = text[6:].strip()

        if "youtube.com" not in url and "youtu.be" not in url:
            await update.message.reply_text("Invalid YouTube link")
            return

        msg = await update.message.reply_text("🎧 Downloading audio...")

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "audio_%(id)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "noplaylist": True,
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_name = f"audio_{info['id']}.mp3"

            with open(file_name, "rb") as audio:
                await update.message.reply_audio(audio=audio, title=info.get("title", "Audio"))

            os.remove(file_name)
            await msg.delete()

        except Exception as e:
            await msg.edit_text(f"Audio Error:\n{e}")

    elif text.lower().startswith(".music"):
        song = text[6:].strip()

        if not song:
            await update.message.reply_text("Example:\n.music faded alan walker")
            return

        msg = await update.message.reply_text("🎵 Searching music...")

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "music_%(id)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
                "noplaylist": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{song}", download=True)

                if "entries" in info:
                    info = info["entries"][0]

                file_name = f"music_{info['id']}.mp3"

            with open(file_name, "rb") as music:
                await update.message.reply_audio(
                    audio=music,
                    title=info.get("title", song)
                )

            os.remove(file_name)
            await msg.delete()

        except Exception as e:
            await msg.edit_text(f"Music Error:\n{e}")

    else:
        await update.message.reply_text("❌ Unknown command\nUse /start")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("BOT RUNNING ✅")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
