# ArchMusic/plugins/start.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ArchMusic import app
import config

START_TEXT = """
🎵 **Pars Müzik Bot** aktif!

✅ YouTube • Spotify • SoundCloud
✅ Hızlı ses sistemi • HD kalite
✅ Kolay kullanım • Premium tasarım

🎧 Yardım için: **/help**
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🎧 Menü", callback_data="settings_helper"),
            InlineKeyboardButton("📚 Komutlar", callback_data="help_cmd")
        ],
        [
            InlineKeyboardButton("🎵 Müzik Grubumuz", url="https://t.me/Pars_Sohbet_TR")
        ],
        [
            InlineKeyboardButton("👑 Sahip", url="https://t.me/Prensesmuzik_kurucu")
        ]
    ]
)

@app.on_message(filters.command(["start", "başla"]))
async def start_command(_, message):
    await message.reply_photo(
        photo="https://telegra.ph/file/59ba9fde5240c1a80bdfa.jpg",  # İstersen bunu değiştirebiliriz
        caption=START_TEXT,
        reply_markup=START_BUTTONS
    )
