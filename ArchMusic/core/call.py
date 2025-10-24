# -*- coding: utf-8 -*-
#
# ArchMusic - Call Controller (Fix)
#

import asyncio
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserAlreadyParticipant, UserNotParticipant
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall, TelegramServerError
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped

import config
from strings import get_string
from ArchMusic import LOGGER, YouTube, app
from ArchMusic.misc import db
from ArchMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_audio_bitrate,
    get_lang,
    get_loop,
    get_video_bitrate,
    group_assistant,
    is_autoend,
    music_on,
    mute_off,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ArchMusic.utils.exceptions import AssistantErr

# 🔧 ÖNEMLİ: inline.play içinden telegram_markup yoksa audio_markup'u alias yapıyoruz
from ArchMusic.utils.inline.play import (
    stream_markup,
    audio_markup as telegram_markup,  # ← alias
)

# Otomatik sonlandırma sayaçları
autoend = {}
counter = {}
AUTO_END_TIME = 3  # dakika


async def _clear_(chat_id: int):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    """Sesli sohbet ve yardımcı (assistant) yönetimi"""

    def __init__(self):
        # 1. string
        self.userbot1 = Client(
            "ArchMusicString1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1 or ""),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)

        # 2. string
        self.userbot2 = Client(
            "ArchMusicString2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2 or ""),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=100)

        # 3. string
        self.userbot3 = Client(
            "ArchMusicString3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3 or ""),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=100)

        # 4. string
        self.userbot4 = Client(
            "ArchMusicString4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4 or ""),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=100)

        # 5. string
        self.userbot5 = Client(
            "ArchMusicString5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5 or ""),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    # ======== Basit kontrol eylemleri ========
    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def mute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.mute_stream(chat_id)

    async def unmute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.unmute_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except Exception:
            pass

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except Exception:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except Exception:
            pass

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        a_q = await get_audio_bitrate(chat_id)
        v_q = await get_video_bitrate(chat_id)
        stream = (
            AudioVideoPiped(link, audio_parameters=a_q, video_parameters=v_q)
            if video
            else AudioPiped(link, audio_parameters=a_q)
        )
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        a_q = await get_audio_bitrate(chat_id)
        v_q = await get_video_bitrate(chat_id)
        stream = (
            AudioVideoPiped(
                file_path,
                audio_parameters=a_q,
                video_parameters=v_q,
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else AudioPiped(
                file_path,
                audio_parameters=a_q,
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        await assistant.change_stream(chat_id, stream)

    async def stream_call(self, link: str):
        """LOG_GROUP_ID üstünden linki hızlıca stream edip çıkmak için mini yardımcı."""
        assistant = await group_assistant(self, config.LOG_GROUP_ID)
        await assistant.join_group_call(
            config.LOG_GROUP_ID,
            AudioVideoPiped(link),
            stream_type=StreamType().pulse_stream,
        )
        await asyncio.sleep(0.5)
        await assistant.leave_group_call(config.LOG_GROUP_ID)

    # ======== Asistanı gruba alma ========
    async def join_assistant(self, original_chat_id: int, chat_id: int):
        language = await get_lang(original_chat_id)
        _ = get_string(language)

        userbot = await get_assistant(chat_id)
        try:
            try:
                get = await app.get_chat_member(chat_id, userbot.id)
            except ChatAdminRequired:
                raise AssistantErr(_["call_1"])  # Yönetici izni yok

            if get.status in (ChatMemberStatus.BANNED, ChatMemberStatus.LEFT):
                raise AssistantErr(_["call_2"].format(userbot.username, userbot.id))

        except UserNotParticipant:
            chat = await app.get_chat(chat_id)
            if chat.username:  # herkese açık grup
                try:
                    await userbot.join_chat(chat.username)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise AssistantErr(_["call_3"].format(e))
            else:  # özel/grup davet linki gerekir
                try:
                    try:
                        invitelink = chat.invite_link or await app.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        raise AssistantErr(_["call_4"])
                    except Exception as e:
                        raise AssistantErr(e)

                    m = await app.send_message(original_chat_id, _["call_5"])
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                    await asyncio.sleep(1.5)
                    await userbot.join_chat(invitelink)
                    await asyncio.sleep(2)
                    await m.edit(_["call_6"].format(userbot.name))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise AssistantErr(_["call_3"].format(e))

    # ======== Çağrıya katıl ve akışı başlat ========
    async def join_call(self, chat_id: int, original_chat_id: int, link: str, video: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        a_q = await get_audio_bitrate(chat_id)
        v_q = await get_video_bitrate(chat_id)

        stream = (
            AudioVideoPiped(link, audio_parameters=a_q, video_parameters=v_q)
            if video
            else AudioPiped(link, audio_parameters=a_q)
        )

        try:
            await assistant.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        except NoActiveGroupCall:
            # Önce asistana gruba girme izni verdir
            await self.join_assistant(original_chat_id, chat_id)
            try:
                await assistant.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
            except Exception:
                raise AssistantErr(
                    "**Aktif Sesli Sohbet Bulunamadı**\n\n"
                    "Lütfen grubun sesli sohbetini açın. Açık ise kapatıp yeniden başlatın. "
                    "Sorun sürerse /restart deneyin."
                )
        except AlreadyJoinedError:
            raise AssistantErr(
                "**Asistan Zaten Sesli Sohbette**\n\n"
                "Genellikle iki sorgu aynı anda yürütüldüğünde olur. "
                "Sesli sohbeti kapatıp yeniden başlatın; devam ederse /restart deneyin."
            )
        except TelegramServerError:
            raise AssistantErr(
                "**Telegram Sunucu Hatası**\n\n"
                "Biraz sonra tekrar deneyin. Sık olursa sesli sohbeti kapatıp yeniden başlatın."
            )

        await add_active_chat(chat_id)
        await mute_off(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

        # Otomatik sonlandırma
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)

    # ======== Sıradaki parçaya geç ========
    async def change_stream(self, client: PyTgCalls, chat_id: int):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)

        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)

            if popped:
                # AUTO_DOWNLOADS_CLEAR aktifse indirilen dosyayı temizleyebilirsin (opsiyonel)
                pass

            if not check:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
        except Exception:
            try:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
            except Exception:
                return

        # Sıradaki
        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        a_q = await get_audio_bitrate(chat_id)
        v_q = await get_video_bitrate(chat_id)
        videoid = check[0]["vidid"]
        check[0]["played"] = 0

        # Kaynak tipine göre akış oluştur
        def _mk_stream(src_link, is_video: bool):
            return (
                AudioVideoPiped(src_link, audio_parameters=a_q, video_parameters=v_q)
                if is_video
                else AudioPiped(src_link, audio_parameters=a_q)
            )

        try:
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(original_chat_id, text=_["call_9"])
                await client.change_stream(chat_id, _mk_stream(link, str(streamtype) == "video"))
                # Telegram tarzı basit panel
                button = telegram_markup(_, chat_id)
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=_["stream_1"].format(
                        title,
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=None,
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"

            elif "vid_" in queued:
                # YouTube indirilen dosya
                mystic = await app.send_message(original_chat_id, _["call_10"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid, mystic, videoid=True, video=True if str(streamtype) == "video" else False
                    )
                except Exception:
                    return await mystic.edit_text(_["call_9"], disable_web_page_preview=True)

                await client.change_stream(chat_id, _mk_stream(file_path, str(streamtype) == "video"))
                await mystic.delete()
                button = stream_markup(_, videoid, chat_id)
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=_["stream_1"].format(
                        title,
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=None,
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

            elif "index_" in queued:
                # m3u8/https direkt link
                await client.change_stream(chat_id, _mk_stream(videoid, str(streamtype) == "video"))
                button = telegram_markup(_, chat_id)
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=_["stream_2"].format(
                        title,
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=None,
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"

            else:
                # telegram/soundcloud/dosya yolu
                await client.change_stream(chat_id, _mk_stream(queued, str(streamtype) == "video"))

                if videoid in ("telegram", "soundcloud"):
                    button = telegram_markup(_, chat_id)
                    run = await app.send_message(
                        original_chat_id,
                        text=_["stream_3"].format(title, check[0]["dur"], user),
                        reply_markup=None,
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    # varsayılan panel
                    button = stream_markup(_, videoid, chat_id)
                    run = await app.send_message(
                        original_chat_id,
                        text=_["stream_1"].format(
                            title,
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=None,
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

        except Exception:
            return await app.send_message(original_chat_id, text=_["call_9"])


# Plugin'lerin beklediği isim: ArchMusic (instance)
ArchMusic = Call()
