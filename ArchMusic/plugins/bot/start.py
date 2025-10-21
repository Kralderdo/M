# Copyright (C) 2021-2023 by ArchBots@Github
# This file is part of < https://github.com/ArchBots/ArchMusic >
# Released under GNU v3.0 License

import asyncio
from typing import Optional, Tuple

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from config.config import OWNER_ID
from strings import get_command, get_string
from ArchMusic import Telegram, YouTube, app
from ArchMusic.misc import SUDOERS
from ArchMusic.plugins.play.playlist import del_plist_msg
from ArchMusic.plugins.sudo.sudoers import sudoers_list
from ArchMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_assistant,
    get_lang,
    get_userss,
    is_on_off,
    is_served_private_chat,
)
from ArchMusic.utils.decorators.language import LanguageStart
from ArchMusic.utils.inline import (
    help_pannel,
    private_panel,
    start_pannel,
)

loop = asyncio.get_running_loop()


def _safe_owner_id() -> Optional[int]:
    """
    OWNER_ID config'ini güvenli şekilde döndürür.
    - OWNER_ID bir liste olmalı (örn: "6366762649 123456789")
    - Boşsa None döner
    """
    try:
        if isinstance(OWNER_ID, (list, tuple)) and len(OWNER_ID) > 0:
            return int(OWNER_ID[0])
    except Exception:
        pass
    return None


@app.on_message(
    filters.command(get_command("START_COMMAND"))
    & filters.private
    & ~BANNED_USERS
)
@LanguageStart
async def start_comm(client, message: Message, _):
    # Kullanıcıyı served listesine ekle (istatistik, vb.)
    try:
        await add_served_user(message.from_user.id)
    except Exception:
        # Bu hata kritik değil; sessiz geçebilir
        pass

    # /start argümanlı mı?
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # /start help
        if name[0:4] == "help":
            try:
                keyboard = help_pannel(_)
                return await message.reply_text(_["help_1"], reply_markup=keyboard)
            except Exception:
                return await message.reply_text(_["help_1"])

        # /start song
        if name[0:4] == "song":
            return await message.reply_text(_["song_2"])

        # /start sta (user stats)
        if name[0:3] == "sta":
            m = await message.reply_text("🔎 Kişisel istatistikleriniz alınıyor…")
            try:
                stats = await get_userss(message.from_user.id)
                tot = len(stats)
                if not stats:
                    await asyncio.sleep(1)
                    return await m.edit(_["ustats_1"])

                def get_stats() -> Tuple[Optional[str], str]:
                    msg = ""
                    limit = 0
                    results = {}
                    for i in stats:
                        top_list = stats[i]["spot"]
                        results[str(i)] = top_list
                    list_arranged = dict(
                        sorted(results.items(), key=lambda item: item[1], reverse=True)
                    )
                    if not list_arranged:
                        return None, _["ustats_1"]
                    tota = 0
                    videoid = None
                    for vidid, count in list_arranged.items():
                        tota += count
                        if limit == 10:
                            continue
                        if limit == 0:
                            videoid = vidid
                        limit += 1
                        details = stats.get(vidid, {})
                        title = (details.get("title", "")[:35]).title()
                        if vidid == "telegram":
                            msg += (
                                "🔗[Telegram Files and Audios]"
                                "(https://t.me/telegram) ** played {c} times**\n\n"
                            ).format(c=count)
                        else:
                            msg += (
                                f"🔗 [{title}](https://www.youtube.com/watch?v={vidid})"
                                f" ** played {count} times**\n\n"
                            )
                    msg = _["ustats_2"].format(tot, tota, min(limit, 10)) + msg
                    return videoid, msg

                try:
                    videoid, msg = await loop.run_in_executor(None, get_stats)
                except Exception:
                    videoid, msg = None, _["ustats_1"]

                await m.delete()
                if videoid:
                    try:
                        thumbnail = await YouTube.thumbnail(videoid, True)
                        return await message.reply_photo(photo=thumbnail, caption=msg)
                    except Exception:
                        pass
                return await message.reply_text(msg)
            except Exception:
                try:
                    return await m.edit(_["ustats_1"])
                except Exception:
                    return

        # /start sud (sudo listesi kısayol)
        if name[0:3] == "sud":
            try:
                await sudoers_list(client=client, message=message, _=_)
            finally:
                if await is_on_off(config.LOG):
                    try:
                        sender_id = message.from_user.id
                        sender_name = message.from_user.first_name
                        await app.send_message(
                            config.LOG_GROUP_ID,
                            f"{message.from_user.mention} az önce <code>SUDOLIST</code>'i kontrol etmek için botu başlattı\n\n"
                            f"**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
                        )
                    except Exception:
                        pass
            return

        # /start lyr (lyrics cache)
        if name[0:3] == "lyr":
            query = (str(name)).replace("lyrics_", "", 1)
            lyrical = getattr(config, "lyrical", {})
            lyrics = lyrical.get(query)
            if lyrics:
                return await Telegram.send_split_text(message, lyrics)
            return await message.reply_text("Şarkı sözleri alınamadı.")

        # /start del (playlist msg cleanup)
        if name[0:3] == "del":
            return await del_plist_msg(client=client, message=message, _=_)

        # /start inf (YouTube info preview)
        if name[0:3] == "inf":
            m = await message.reply_text("🔎 Bilgi Alınıyor!")
            try:
                query = (str(name)).replace("info_", "", 1)
                query = f"https://www.youtube.com/watch?v={query}"
                results = VideosSearch(query, limit=1)
                title = duration = views = thumbnail = channellink = channel = link = published = None
                for result in (await results.next())["result"]:
                    title = result.get("title")
                    duration = result.get("duration")
                    views = result.get("viewCount", {}).get("short")
                    thumb_url = result.get("thumbnails", [{}])[0].get("url", "")
                    thumbnail = thumb_url.split("?")[0] if thumb_url else None
                    channellink = result.get("channel", {}).get("link")
                    channel = result.get("channel", {}).get("name")
                    link = result.get("link")
                    published = result.get("publishedTime")
                searched_text = f"""
🔍__**Video Parça Bilgisi**__

❇️**Başlık:** {title}

⏳**Süre:** {duration} Dakika
👀**Görüntülemeler:** `{views}`
⏰**Yayınlanma Zamanı:** {published}
🎥**Kanal Adı:** {channel}
📎**Kanal Bağlantısı:** [Buradan Ziyaret Edin]({channellink})
🔗**Video Bağlantısı:** [Bağlantı]({link})

⚡️ __Aranan Destekçi: {config.MUSIC_BOT_NAME}__"""
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="🎥 İzle ", url=f"{link}"),
                            InlineKeyboardButton(text="🔄 Kapat", callback_data="close"),
                        ],
                    ]
                )
                await m.delete()
                if thumbnail:
                    await app.send_photo(
                        message.chat.id,
                        photo=thumbnail,
                        caption=searched_text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=key,
                    )
                else:
                    await message.reply_text(
                        searched_text, parse_mode=ParseMode.MARKDOWN, reply_markup=key
                    )
                if await is_on_off(config.LOG):
                    try:
                        sender_id = message.from_user.id
                        sender_name = message.from_user.first_name
                        await app.send_message(
                            config.LOG_GROUP_ID,
                            f"{message.from_user.mention} az önce <code>VİDEO BİLGİLERİ</code>'ni kontrol etmek için botu başlattı\n\n"
                            f"**KULLANICI Kimliği:** {sender_id}\n**KULLANICI ADI:** {sender_name}",
                        )
                    except Exception:
                        pass
                return
            except Exception:
                try:
                    await m.edit("Şarkı bilgisi alınamadı.")
                except Exception:
                    pass
                return

        # Tanınmayan /start parametresi → sessiz geç
        return

    # --- Argümansız /start akışı ---
    try:
        # PRO FIX: resolve_peer kaldırıldı (botlarda yasak). OWNER_ID güvenli okunuyor.
        OWNER = _safe_owner_id()
        out = private_panel(_, app.username, OWNER)
    except Exception:
        OWNER = None
        out = private_panel(_, app.username, OWNER)

    if config.START_IMG_URL:
        try:
            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["start_2"].format(config.MUSIC_BOT_NAME),
                reply_markup=InlineKeyboardMarkup(out),
            )
        except Exception:
            await message.reply_text(
                _["start_2"].format(config.MUSIC_BOT_NAME),
                reply_markup=InlineKeyboardMarkup(out),
            )
    else:
        await message.reply_text(
            _["start_2"].format(config.MUSIC_BOT_NAME),
            reply_markup=InlineKeyboardMarkup(out),
        )

    if await is_on_off(config.LOG):
        try:
            sender_id = message.from_user.id
            sender_name = message.from_user.first_name
            await app.send_message(
                config.LOG_GROUP_ID,
                f"{message.from_user.mention}, Bot'u yeni başlattı.\n\n"
                f"**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
            )
        except Exception:
            pass


# ---- Yeni Üye Karşılama ----
welcome_group = 2


@app.on_message(filters.new_chat_members, group=welcome_group)
async def welcome(client, message: Message):
    chat_id = message.chat.id

    # Private bot modu kontrolü
    if str(config.PRIVATE_BOT_MODE) == str(True):
        try:
            if not await is_served_private_chat(message.chat.id):
                await message.reply_text(
                    "**Özel Müzik Botu**\n\n"
                    "Yalnızca sahibinden gelen yetkili sohbetler için. "
                    "Önce sahibimden sohbetinize izin vermesini isteyin."
                )
                return await app.leave_chat(message.chat.id)
        except Exception:
            # En kötü ihtimal: oda izinli değilse gruptan ayrıl
            try:
                return await app.leave_chat(message.chat.id)
            except Exception:
                return
    else:
        try:
            await add_served_chat(chat_id)
        except Exception:
            pass

    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            # Botun kendisi eklendiyse
            if member.id == app.id:
                chat_type = message.chat.type
                if chat_type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_6"])
                    return await app.leave_chat(message.chat.id)

                # Kara liste kontrolü
                try:
                    if chat_id in await blacklisted_chats():
                        await message.reply_text(
                            _["start_7"].format(
                                f"https://t.me/{app.username}?start=sudolist"
                            )
                        )
                        return await app.leave_chat(chat_id)
                except Exception:
                    pass

                # Asistan ve start paneli
                try:
                    userbot = await get_assistant(message.chat.id)
                except Exception:
                    userbot = None

                out = start_pannel(_)

                # Karşılama videosu (isteğe bağlı)
                video_url = "https://telegra.ph/file/acfb445238b05315f0013.mp4"
                video_caption = _["start_3"].format(
                    config.MUSIC_BOT_NAME,
                    getattr(userbot, "username", "assistant"),
                    getattr(userbot, "id", 0),
                )

                try:
                    await app.send_video(
                        message.chat.id,
                        video_url,
                        caption=video_caption,
                        reply_markup=InlineKeyboardMarkup(out),
                    )
                except Exception:
                    # Video gönderilemezse text fallback
                    try:
                        await message.reply_text(video_caption, reply_markup=InlineKeyboardMarkup(out))
                    except Exception:
                        pass

            # Owner ve SUDO etiketli karşılama
            if member.id in getattr(config, "OWNER_ID", []):
                return await message.reply_text(
                    _["start_4"].format(config.MUSIC_BOT_NAME, member.mention)
                )
            if member.id in SUDOERS:
                return await message.reply_text(
                    _["start_5"].format(config.MUSIC_BOT_NAME, member.mention)
                )
            return
        except Exception:
            # Bu handler gruba engel olmasın diye sessizce geç
            return
