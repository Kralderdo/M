# Copyright (C) 2021-2023 by ArchBots@Github
# This file is part of ArchMusic (GNU v3.0)

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, MONGO_DB_URI, OWNER_ID
from strings import get_command
from ArchMusic import app
from ArchMusic.misc import SUDOERS
from ArchMusic.utils.database import add_sudo, remove_sudo
from ArchMusic.utils.decorators.language import language

# Commands
ADDSUDO_COMMAND = get_command("ADDSUDO_COMMAND")
DELSUDO_COMMAND = get_command("DELSUDO_COMMAND")
SUDOUSERS_COMMAND = get_command("SUDOUSERS_COMMAND")


# ---- Yardımcı: hedef kullanıcıyı güvenli çöz ----
async def _safe_resolve_user_id(raw: str) -> int:
    """
    - '@user' -> username
    - '123456789' (str) -> INT'e çevir (phone sanılmasın)
    - 'me', 'self' gibi destekli özel değerler Pyrogram tarafından zaten çözülür,
      ama biz burada sadece int/username yolundan gideriz.
    """
    user_key = raw.strip()

    # username temizliği
    if user_key.startswith("@"):
        user_key = user_key[1:]

    # saf rakamsa: INT'e çevir → phone resolve tetiklenmez
    if user_key.isdigit():
        uid = int(user_key)
        user = await app.get_users(uid)
        return user.id

    # rakam değilse username kabul et
    user = await app.get_users(user_key)
    return user.id


@app.on_message(filters.command(ADDSUDO_COMMAND) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if not MONGO_DB_URI:
        return await message.reply_text(
            _["general_1"]  # mevcut çeviri: eksik değişken uyarısı
            if "general_1" in _
            else "**Bu özellik için MONGO_DB_URI gerekli.**"
        )

    # reply ile ekleme
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id

    else:
        # /addsudo <id|@username>
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        raw = message.text.split(None, 1)[1]
        try:
            target_id = await _safe_resolve_user_id(raw)
        except Exception:
            return await message.reply_text(
                _["sudo_8"] if "sudo_8" in _ else "Kullanıcı çözümlenemedi."
            )

    if target_id in SUDOERS:
        return await message.reply_text(
            _["sudo_1"].format(message.reply_to_message.from_user.mention)
            if message.reply_to_message
            else _["sudo_1"].format("**kullanıcı**")
        )

    added = await add_sudo(target_id)
    if added:
        SUDOERS.add(target_id)  # RAM senkron
        try:
            user_obj = await app.get_users(target_id)
            mention = user_obj.mention
        except Exception:
            mention = f"`{target_id}`"
        return await message.reply_text(_["sudo_2"].format(mention))
    return await message.reply_text("Failed")


@app.on_message(filters.command(DELSUDO_COMMAND) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if not MONGO_DB_URI:
        return await message.reply_text(
            _["general_1"]
            if "general_1" in _
            else "**Bu özellik için MONGO_DB_URI gerekli.**"
        )

    # reply ile silme
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    else:
        # /delsudo <id|@username>
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
        raw = message.text.split(None, 1)[1]
        try:
            target_id = await _safe_resolve_user_id(raw)
        except Exception:
            return await message.reply_text(
                _["sudo_8"] if "sudo_8" in _ else "Kullanıcı çözümlenemedi."
            )

    # OWNER koruması
    try:
        if isinstance(OWNER_ID, (list, tuple)):
            if target_id in OWNER_ID:
                return await message.reply_text(
                    _["sudo_9"] if "sudo_9" in _ else "Sahibi sudo listesinden kaldıramazsın."
                )
        elif isinstance(OWNER_ID, int) and target_id == OWNER_ID:
            return await message.reply_text(
                _["sudo_9"] if "sudo_9" in _ else "Sahibi sudo listesinden kaldıramazsın."
            )
    except Exception:
        pass

    if target_id not in SUDOERS:
        return await message.reply_text(_["sudo_3"])

    removed = await remove_sudo(target_id)
    if removed:
        # RAM senkron
        if target_id in SUDOERS:
            SUDOERS.remove(target_id)
        return await message.reply_text(_["sudo_4"])

    # detaylı geri bildirim
    return await message.reply_text(
        _["sudo_10"] if "sudo_10" in _ else "Bir şeyler ters gitti, silinemedi."
    )


@app.on_message(filters.command(SUDOUSERS_COMMAND) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    text = _["sudo_5"]
    count = 0

    # OWNER'lar
    owners = OWNER_ID if isinstance(OWNER_ID, (list, tuple)) else [OWNER_ID]
    for x in owners:
        try:
            user = await app.get_users(x)
            name = user.mention or user.first_name
            count += 1
            text += f"{count}➤ {name}\n"
        except Exception:
            continue

    # SUDOERS (OWNER hariç)
    smex = 0
    for user_id in list(SUDOERS):
        if user_id in owners:
            continue
        try:
            user = await app.get_users(user_id)
            name = user.mention or user.first_name
            if smex == 0:
                smex += 1
                text += _["sudo_6"]
            count += 1
            text += f"{count}➤ {name}\n"
        except Exception:
            continue

    if count == 0:
        return await message.reply_text(_["sudo_7"])
    return await message.reply_text(text)
