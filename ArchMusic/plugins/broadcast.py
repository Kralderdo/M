from pyrogram import Client, filters
from pyrogram.types import Message
from ArchMusic import app
from config import SUDO_USERS

# /broadcast komutu sadece owner veya sudo kullanıcıları için aktif
@app.on_message(filters.command("broadcast") & filters.user(SUDO_USERS))
async def broadcast_message(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Kullanım: /broadcast <mesaj>")
    
    text = message.text.split(None, 1)[1]
    sent = 0
    failed = 0

    await message.reply_text("📢 Yayın başlatıldı...")

    async for dialog in client.get_dialogs():
        try:
            await client.send_message(dialog.chat.id, text)
            sent += 1
        except Exception:
            failed += 1
            continue

    await message.reply_text(
        f"✅ **Broadcast tamamlandı!**\n\n📬 Başarılı: {sent}\n❌ Başarısız: {failed}"
  )
