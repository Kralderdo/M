from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from ArchMusic import app
import config
import time

# -------------------- START MESAJI --------------------

START_TEXT = f"""
✅ **{config.MUSIC_BOT_NAME} aktif!**

Merhaba, ben müzik çalma botuyum 🎧  
Grup sesli sohbetlerinde kaliteli müzik çalabilirim!

ℹ️ Komutları görmek için aşağıdaki menüyü kullanın.
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("📚 Komutlar", callback_data="help_menu")],
        [
            InlineKeyboardButton("💬 Destek", url=config.SUPPORT_GROUP),
            InlineKeyboardButton("📢 Kanal", url=config.SUPPORT_CHANNEL)
        ]
    ]
)


@app.on_message(filters.command("start") & filters.private)
async def start_private(client, message):
    await message.reply_text(START_TEXT, reply_markup=START_BUTTONS)


@app.on_message(filters.command("start") & filters.group)
async def start_group(client, message):
    await message.reply_text(f"✅ **{config.MUSIC_BOT_NAME} çalışıyor!** 🎶")

# -------------------- HELP MENÜ --------------------

HELP_TEXT = """
🎛 **Komut Menüsü**

🎵 **Müzik**
/oynat <şarkı> - Şarkı çalar
/atla - Sonrakine geç
/duraklat - Durdur
/devam - Devam et
/son - Müzik kapat

⚙️ **Yönetim**
/yardim - Yardım menüsü
/ping - Bot hızını ölçer
/alive - Bot durumu
"""


HELP_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="start_back")]])


@app.on_callback_query(filters.regex("help_menu"))
async def help_menu(_, query: CallbackQuery):
    await query.message.edit_text(HELP_TEXT, reply_markup=HELP_BUTTONS)


@app.on_callback_query(filters.regex("start_back"))
async def start_back(_, query: CallbackQuery):
    await query.message.edit_text(START_TEXT, reply_markup=START_BUTTONS)

# -------------------- PING --------------------

@app.on_message(filters.command("ping"))
async def ping(_, message):
    start = time.time()
    reply = await message.reply_text("🏓 Ping...")
    end = time.time()
    await reply.edit_text(f"🏓 **Pong!** `{round((end - start) * 1000)} ms`")

# -------------------- ALIVE --------------------

@app.on_message(filters.command("alive"))
async def alive(_, message):
    await message.reply_text(
        f"✅ **{config.MUSIC_BOT_NAME} aktif!**\n"
        f"👑 Sahibim: `{config.OWNER_ID}`\n"
        "⚙️ Sistem: Pyrogram + PyTgCalls\n"
        "📚 Yardım: /help"
    )

# -------------------- HELP KOMUTU --------------------

@app.on_message(filters.command("help"))
async def help_cmd(_, message):
    await message.reply_text(HELP_TEXT, reply_markup=HELP_BUTTONS)
