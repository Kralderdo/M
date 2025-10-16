from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_GROUP_ID
from ArchMusic import app


async def new_message(chat_id: int, message: str, reply_markup=None):
    try:
        await app.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    except Exception as e:
        if "BUTTON_USER_PRIVACY_RESTRICTED" in str(e):
            await app.send_message(
                chat_id=chat_id,
                text="⚠️ Gizlilik nedeniyle kullanıcı profiline buton oluşturulamadı.",
            )
        else:
            raise


@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    me = await client.get_me()
    new_users = [user.id for user in message.new_chat_members]

    if me.id in new_users:
        added_by = message.from_user.first_name
        chatusername = f"@{message.chat.username}" if message.chat.username else "Yok"
        title = message.chat.title
        chat_id = message.chat.id

        sigma = (
            f"<u>#**Yeni Gruba Eklendi**</u> :\n\n"
            f"**Grup ID:** {chat_id}\n"
            f"**Grup Adı:** {title}\n"
            f"**Grup Link:** {chatusername}\n"
            f"**Gruba Ekleyen:** {added_by}"
        )

        # user_id yerine URL kullanıyoruz
        url = f"https://t.me/{message.from_user.username}" if message.from_user.username else None
        buttons = [[InlineKeyboardButton(added_by, url=url)]] if url else None

        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        await new_message(LOG_GROUP_ID, sigma, reply_markup)


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client: Client, message: Message):
    me = await client.get_me()

    if me.id == message.left_chat_member.id:
        removed_by = message.from_user.first_name
        title = message.chat.title
        chat_id = message.chat.id

        bye = (
            f"<u>#**Gruptan Çıkarıldı**</u> :\n\n"
            f"**Grup ID:** {chat_id}\n"
            f"**Grup Adı:** {title}\n"
            f"**Gruptan Çıkaran:** {removed_by}"
        )

        # user_id yerine URL kullanıyoruz
        url = f"https://t.me/{message.from_user.username}" if message.from_user.username else None
        buttons = [[InlineKeyboardButton(removed_by, url=url)]] if url else None

        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        await new_message(LOG_GROUP_ID, bye, reply_markup)
