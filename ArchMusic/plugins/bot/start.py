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
from pyrogram.types import CallbackQuery

HELP_TEXT = """
**🎛 Komut Menüsü**

🎵 **Müzik Komutları**
/play <şarkı adı> - Şarkı çalar
/skip - Şarkıyı geç
/stop - Müzik durdur
/pause - Durdur
/resume - Devam et
/playlist - Aktif listeyi göster

👑 **Yönetici Komutları**
/admincache - Admin listesini yenile
/auth <kullanıcı> - Yetki ver
/unauth <kullanıcı> - Yetki kaldır

⚙️ **Diğer**
/ping - Bot durumu
/help - Yardım
"""

HELP_BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔙 Geri", callback_data="start_back")]
    ]
)

@app.on_callback_query(filters.regex("help_menu"))
async def help_menu(_, query: CallbackQuery):
    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=HELP_BUTTONS
    )

@app.on_callback_query(filters.regex("start_back"))
async def start_back(_, query: CallbackQuery):
    await query.message.edit_text(
        START_TEXT,
        reply_markup=START_BUTTONS
)
    from pyrogram import filters
from ArchMusic import app
import time

@app.on_message(filters.command("ping"))
async def ping(_, message):
    start = time.time()
    reply = await message.reply_text("🔄 Ping ölçülüyor...")
    end = time.time()
    await reply.edit_text(f"✅ Pong! `{round((end - start) * 1000)}ms`")

@app.on_message(filters.command("alive"))
async def alive(_, message):
    await message.reply_text(
        f"✅ **{config.MUSIC_BOT_NAME} çalışıyor!**\n"
        f"🛠️ Destekleyen Sistem: Pyrogram + PyTgCalls\n"
        f"👑 Sahip: `{config.OWNER_ID}`\n"
        f"🔧 Yardım için /help"
    )

@app.on_message(filters.command("help"))
async def help_cmd(_, message):
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.reply_text(
        HELP_TEXT,
        reply_markup=HELP_BUTTONS
    )
    
