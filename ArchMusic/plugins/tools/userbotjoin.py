from pyrogram import filters
from pyrogram.types import Message
from config import BANNED_USERS, OWNER_ID
from ArchMusic import app, userbot
from ArchMusic.utils.decorators.language import language

# ✅ Assistant'ı gruba sokan komut
@app.on_message(filters.command(["userbotjoin", "assistant", "katıl"]) & filters.group & ~BANNED_USERS)
@language
async def join_group_chat(client, message: Message, _):
    chat_id = message.chat.id

    try:
        # Eğer assistant zaten gruptaysa
        member = await app.get_chat_member(chat_id, userbot.id)
        if member:
            return await message.reply_text("✅ Asistan zaten bu grupta aktif!")

    except:
        pass

    try:
        # Asistanı davet etmeyi dene
        invite_link = await message.chat.export_invite_link()
        await userbot.join_chat(invite_link)
        await message.reply_text("✅ Asistan gruba başarıyla katıldı!")
    except Exception as e:
        return await message.reply_text(f"⚠️ Asistan katılamadı:\n\n`{e}`\n\n➥ Çözüm: Asistanın kullanıcı adını gruba **manuel ekle** ve tekrar dene.")
