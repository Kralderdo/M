from pyrogram import filters
from pyrogram.types import Message
from ArchMusic import app, userbot

# ✅ Güvenli SUDO_USERS import
try:
    from config import SUDO_USERS
except ImportError:
    SUDO_USERS = []

try:
    from config import OWNER_ID
except ImportError:
    OWNER_ID = None

# ✅ broadcast komutu
@app.on_message(filters.command("broadcast") & filters.user(([OWNER_ID] if OWNER_ID else []) + SUDO_USERS))
async def broadcast_message(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("📢 Kullanım: `/broadcast mesaj`", quote=True)

    text = message.text.split(None, 1)[1]
    sent = 0
    failed = 0
    status = await message.reply_text("📡 Yayın başlatılıyor...")

    async for dialog in userbot.get_dialogs():
        try:
            await userbot.send_message(dialog.chat.id, text)
            sent += 1
        except:
            failed += 1
            continue

    await status.edit_text(
        f"✅ **Broadcast tamamlandı!**\n\n"
        f"📨 Başarıyla gönderildi: `{sent}`\n"
        f"⚠️ Gönderilemedi: `{failed}`"
    )
