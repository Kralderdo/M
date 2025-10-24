from pyrogram import filters
from pyrogram.types import Message
from ArchMusic import app
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils.decorators import authorized_users_only

# Pause
@app.on_message(filters.command(["pause", "duraklat"]) & filters.group)
@authorized_users_only
async def pause_music(_, message: Message):
    await ArchMusic.pause_stream(message.chat.id)
    await message.reply_text("⏸ Müzik duraklatıldı.")

# Resume
@app.on_message(filters.command(["resume", "devam"]) & filters.group)
@authorized_users_only
async def resume_music(_, message: Message):
    await ArchMusic.resume_stream(message.chat.id)
    await message.reply_text("▶️ Müzik devam ediyor.")

# Skip
@app.on_message(filters.command(["skip", "geç"]) & filters.group)
@authorized_users_only
async def skip_music(_, message: Message):
    await ArchMusic.force_stop_stream(message.chat.id)
    await message.reply_text("⏭ Şarkı atlandı, sıradaki geliyor...")

# Stop
@app.on_message(filters.command(["stop", "durdur"]) & filters.group)
@authorized_users_only
async def stop_music(_, message: Message):
    await ArchMusic.stop_stream(message.chat.id)
    await message.reply_text("⛔ Müzik tamamen durduruldu.")

# Mute
@app.on_message(filters.command(["mute", "sessiz"]) & filters.group)
@authorized_users_only
async def mute_music(_, message: Message):
    await ArchMusic.mute_stream(message.chat.id)
    await message.reply_text("🔇 Asistan sessize alındı.")

# Unmute
@app.on_message(filters.command(["unmute", "sesac"]) & filters.group)
@authorized_users_only
async def unmute_music(_, message: Message):
    await ArchMusic.unmute_stream(message.chat.id)
    await message.reply_text("🔊 Asistan sesi açıldı.")
