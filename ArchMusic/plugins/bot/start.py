from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ArchMusic import app
import config

START_TEXT = f"""
✅ **{config.MUSIC_BOT_NAME} aktif!**

Merhaba, ben müzik çalma botuyum.  
Sesli sohbetlerde müzik çalabilir, playlist oluşturabilir ve daha fazlasını yapabilirim!

ℹ️ Komutları görmek için **yardım menüsünü** kullanabilirsiniz.
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("📚 Komutlar", callback_data="help_menu"),
        ],
        [
            InlineKeyboardButton("💬 Destek Grubu", url=config.SUPPORT_GROUP),
            InlineKeyboardButton("📢 Kanal", url=config.SUPPORT_CHANNEL)
        ]
    ]
)

# ✅ Özel sohbet için start
@app.on_message(filters.command("start") & filters.private)
async def start_private(client, message):
    await message.reply_text(
        START_TEXT,
        reply_markup=START_BUTTONS
    )

# ✅ Gruplarda start
@app.on_message(filters.command("start") & filters.group)
async def start_group(client, message):
    await message.reply_text(
        f"✅ **{config.MUSIC_BOT_NAME} çalışıyor!**\n\nKomutlarla devam edebilirsin 🔥"
    )
