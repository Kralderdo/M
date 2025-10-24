from pyrogram import filters
from pyrogram.types import Message
from ArchMusic import app
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils.database import is_music_playing, music_on
from ArchMusic.utils.decorators import authorized_users_only
from ArchMusic.utils.stream.stream import stream

@app.on_message(filters.command(["play", "oynat"]) & filters.group)
@authorized_users_only
async def play_handler(_, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("🎧 Bir şarkı adı yaz veya MP3 dosyası yanıtlayarak çal!")

    query = None
    if message.reply_to_message and message.reply_to_message.audio:
        query = message.reply_to_message.audio.file_id
    else:
        query = message.text.split(None, 1)[1]

    await message.reply_text(f"🔎 **Aranıyor:** `{query}` ...")

    try:
        await stream(message, query)
        await music_on(message.chat.id)
    except Exception as e:
        return await message.reply_text(f"❌ Çalma hatası: `{e}`")
