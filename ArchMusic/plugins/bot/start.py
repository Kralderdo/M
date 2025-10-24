from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ArchMusic import app
import config


START_TEXT = f"""
🎵 **{config.MUSIC_BOT_NAME} aktif!**  
Ben gruplarda müzik çalan gelişmiş bir Telegram botuyum.  
Aşağıdan komutlara göz atabilirsin. 👇
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("📚 Komutlar", callback_data="help_menu"),
            InlineKeyboardButton("🎧 Destek Grubu", url=config.SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton("📢 Kanal", url=config.SUPPORT_CHANNEL)
        ]
    ]
)


@app.on_message(filters.command(["start", "start@pars_muzikbot"]))
async def start_command(client, message):
    await message.reply_text(START_TEXT, reply_markup=START_BUTTONS)
