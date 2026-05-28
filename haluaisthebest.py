import os
import requests
import yt_dlp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

# =========================
# TOKENS
# =========================

BOT_TOKEN = "8819149020:AAH_qW1JO6a2yQBVB0CrJ0rnuwcHvrfRsQQ"

OPENROUTER_API_KEY = "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"

# =========================
# DEEPSEEK API
# =========================

DEEPSEEK_API = "https://deepseekreasoning.suryahacker.workers.dev/?query="

# =========================
# START MENU
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("🤖 AI Chat", callback_data="ai"),
            InlineKeyboardButton("🖼 Image", callback_data="image"),
        ],
        [
            InlineKeyboardButton("🎵 Music", callback_data="music"),
            InlineKeyboardButton("🎧 Audio", callback_data="audio"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = """
🔥 MULTI AI BOT 🔥

Commands:

.ai hello
→ AI Chat

.image wolf in forest
→ Generate Image

.audio YOUTUBE_LINK
→ Video To Audio

.music song name
→ Download Music
"""

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# =========================
# BUTTONS
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "ai":
        await query.message.reply_text(
            ".ai hello"
        )

    elif data == "image":
        await query.message.reply_text(
            ".image wolf with red eyes"
        )

    elif data == "audio":
        await query.message.reply_text(
            ".audio youtube_link"
        )

    elif data == "music":
        await query.message.reply_text(
            ".music faded alan walker"
        )

# =========================
# MAIN MESSAGE HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # =========================
    # AI CHAT
    # =========================

    if text.startswith(".ai"):

        prompt = text.replace(".ai", "").strip()

        if not prompt:
            await update.message.reply_text(
                "Example:\n.ai hello"
            )
            return

        await update.message.reply_text(
            "🤖 Thinking..."
        )

        try:

            url = DEEPSEEK_API + prompt

            response = requests.get(url).json()

            reply = response["result"]["response"]

            await update.message.reply_text(reply)

        except Exception as e:

            await update.message.reply_text(
                f"Error:\n{e}"
            )

    # =========================
    # IMAGE GENERATION
    # =========================

    elif text.startswith(".image"):

        prompt = text.replace(".image", "").strip()

        if not prompt:
            await update.message.reply_text(
                "Example:\n.image cyber wolf"
            )
            return

        await update.message.reply_text(
            "🖼 Generating image..."
        )

        try:

            response = requests.post(
                url="https://openrouter.ai/api/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "x-ai/grok-imagine-image-quality",
                    "prompt": prompt
                }
            )

            data = response.json()

            image_url = data["data"][0]["url"]

            await update.message.reply_photo(
                photo=image_url,
                caption=f"Prompt: {prompt}"
            )

        except Exception as e:

            await update.message.reply_text(
                f"Error:\n{e}"
            )

    # =========================
    # YOUTUBE AUDIO
    # =========================

    elif text.startswith(".audio"):

        url = text.replace(".audio", "").strip()

        if "youtube.com" not in url and "youtu.be" not in url:

            await update.message.reply_text(
                "Invalid YouTube link"
            )
            return

        await update.message.reply_text(
            "🎧 Downloading audio..."
        )

        try:

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "audio.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            file_name = "audio.mp3"

            with open(file_name, "rb") as audio:
                await update.message.reply_audio(audio=audio)

            os.remove(file_name)

        except Exception as e:

            await update.message.reply_text(
                f"Error:\n{e}"
            )

    # =========================
    # MUSIC DOWNLOAD
    # =========================

    elif text.startswith(".music"):

        song = text.replace(".music", "").strip()

        if not song:

            await update.message.reply_text(
                "Example:\n.music faded alan walker"
            )
            return

        await update.message.reply_text(
            "🎵 Searching music..."
        )

        try:

            search_url = f"ytsearch1:{song}"

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "music.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_url])

            with open("music.mp3", "rb") as music:
                await update.message.reply_audio(
                    audio=music,
                    title=song
                )

            os.remove("music.mp3")

        except Exception as e:

            await update.message.reply_text(
                f"Error:\n{e}"
            )

    else:

        await update.message.reply_text(
            "❌ Unknown command\n\nUse /start"
        )

# =========================
# MAIN
# =========================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("BOT RUNNING ✅")

    app.run_polling()

if __name__ == "__main__":
    main()