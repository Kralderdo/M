# Copyright (C) 2021-2023 by ArchBots@Github
# This file is part of ArchMusic (GNU v3.0)

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, MONGO_DB_URI, OWNER_ID
from strings import get_command
from ArchMusic import app
from ArchMusic.misc import SUDOERS
from ArchMusic.utils.database import add_sudo, remove_sudo, get_sudoers
from ArchMusic.utils.decorators.language import language

# Commands
ADDSUDO_COMMAND = get_command("ADDSUDO_COMMAND")
DELSUDO_COMMAND = get_command("DELSUDO_COMMAND")
SUDOUSERS_COMMAND = get_command("SUDOUSERS_COMMAND")


# ---- Hedef kullanıcıyı güvenli çöz ----
async def _safe_resolve_user_id(raw: str) -> int:
    """
    Güvenli çözüm:
      - '@user' -> username
      - '123456789' -> int'e çevir (telefon sanılmasın)
    """
    user_key = raw.strip()
    if user_key.startswith("@"):
        user_key = user_key[1:]

    if user_key.isdigit():
        uid = int(user_key)
        user = await app.get_users(uid)
        return user.id

    user = await app.get_users(user_key)
    return user.id


def _is_owner(uid: int) -> bool:
    try:
        if isinstance(OWNER_ID, (list, tuple)):
            return uid in OWNER_ID
        return uid == OWNER_ID
    except Exception:
        return False


@app.on_message(filters.command(ADDSUDO_COMMAND) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if not MONGO_DB_URI:
        return await message.reply_text(
            _["general_1"] if "general_1" in _ else "**Bu özellik için MONGO_DB_URI gerekli.**"
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

    # Zaten sudo mu?
    if target_id in SUDOERS or target_id in await get_sudoers():
        try:
            u = await app.get_users(target_id)
            mention = u.mention
        except Exception:
            mention = f"`{target_id}`"
        return await message.reply_text(_["sudo_1"].format(mention))

    added = await add_sudo(target_id)
    if added:
        SUDOERS.add(target_id)  # RAM senkron
        try:
            u = await app.get_users(target_id)
            mention = u.mention
        except Exception:
            mention = f"`{target_id}`"
        return await message.reply_text(_["sudo_2"].format(mention))

    return await message.reply_text("Failed")


@app.on_message(filters.command(DELSUDO_COMMAND) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if not MONGO_DB_URI:
        return await message.reply_text(
            _["general_1"] if "general_1" in _ else "**Bu özellik için MONGO_DB_URI gerekli.**"
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
    if _is_owner(target_id):
        return await message.reply_text(
            _["sudo_9"] if "sudo_9" in _ else "Sahibi sudo listesinden kaldıramazsın."
        )

    # Üyelik kontrolünü DB'den yap (RAM uyuşmazlığı silmeyi engellemesin)
    db_sudos = await get_sudoers()
    if target_id not in db_sudos:
        return await message.reply_text(_["sudo_3"])  # "Sudo parçası değil"

    removed = await remove_sudo(target_id)
    if removed:
        # RAM senkron: listede varsa çıkar
        try:
            SUDOERS.discard(target_id)
        except Exception:
            pass
        return await message.reply_text(_["sudo_4"])  # "Sudo'dan kaldırıldı"

    # Hâlâ buraya düştüyse DB yazılamadı
    return await message.reply_text(
        _["sudo_10"] if "sudo_10" in _ else "Bir şeyler ters gitti, silinemedi."
    )


@app.on_message(filters.command(SUDOUSERS_COMMAND) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    text = _["sudo_5"]  # başlık
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

    # SUDOERS (DB'den) - OWNER hariç
    db_sudos = await get_sudoers()
    others_added = False
    for uid in db_sudos:
        if uid in owners:
            continue
        try:
            user = await app.get_users(uid)
            name = user.mention or user.first_name
            if not others_added:
                text += _["sudo_6"]  # "SUDO USERS:"
                others_added = True
            count += 1
            text += f"{count}➤ {name}\n"
        except Exception:
            continue

    if count == 0:
        return await message.reply_text(_["sudo_7"])  # "Sudo yok"
    return await message.reply_text(text)
