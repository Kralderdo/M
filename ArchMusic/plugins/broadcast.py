from pyrogram import filters
from pyrogram.types import Message
from ArchMusic import app, userbot
from config import OWNER_ID, SUDO_USERS

@app.on_message(filters.command("broadcast") & filters.user([OWNER_ID] + SUDO_USERS))
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
        f"✅ Broadcast tamamlandı!\n\n"
        f"📨 Gönderildi: `{sent}`\n"
        f"⚠️ Hata: `{failed}`"
    )
