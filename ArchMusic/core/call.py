# ArchMusic/core/call.py
# Tek-Asistan Stabil Sürüm (STRING1)

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

# Bazı modüller telegram_markup bekliyor; audio panelini aliaslıyoruz.
from ArchMusic.utils.inline.play import (
    stream_markup,
    audio_markup as telegram_markup,
)

autoend = {}
counter = {}
AUTO_END_TIME = 3  # dakika


async def _clear_(chat_id: int):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call:
    """
    Tek-asistan mimarisi (STRING1).
    """

    def __init__(self):
        # PYROGRAM USERBOT (Assistant)
        self.userbot1 = Client(
            "ArchMusicString1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        # PyTgCalls
        self.one = PyTgCalls(self.userbot1, cache_duration=100)

        # Uyumluluk alanları
        self.two = None
        self.three = None
        self.four = None
        self.five = None

    async def _assistant_client(self, chat_id: int) -> PyTgCalls:
        # Çoklu-asistan arayan yardımcılarla uyum için.
        return self.one

    # ==== Kontroller ====

    async def pause_stream(self, chat_id: int):
        assistant = await self._assistant_client(chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await self._assistant_client(chat_id)
        await assistant.resume_stream(chat_id)

    async def mute_stream(self, chat_id: int):
        assistant = await self._assistant_client(chat_id)
        await assistant.mute_stream(chat_id)

    async def unmute_stream(self, chat_id: int):
        assistant = await self._assistant_client(chat_id)
        await assistant.unmute_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await self._assistant_client(chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except Exception:
            pass

    async def force_stop_stream(self, chat_id: int):
        assistant = await self._assistant_client(chat_id)
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
        assistant = await self._assistant_client(chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        stream = (
            AudioVideoPiped(link, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality)
            if video else
            AudioPiped(link, audio_parameters=audio_stream_quality)
        )
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id: int, file_path: str, to_seek: int, duration: int, mode: str):
        assistant = await self._assistant_client(chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        stream = (
            AudioVideoPiped(
                file_path,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video" else
            AudioPiped(
                file_path,
                audio_parameters=audio_stream_quality,
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        await assistant.change_stream(chat_id, stream)

    async def stream_call(self, link: str):
        # Log grubunda hızlı join/leave testi
        assistant = await self._assistant_client(config.LOG_GROUP_ID)
        await assistant.join_group_call(
            config.LOG_GROUP_ID,
            AudioVideoPiped(link),
            stream_type=StreamType().pulse_stream,
        )
        await asyncio.sleep(0.5)
        await assistant.leave_group_call(config.LOG_GROUP_ID)

    # ==== Asistanı gruba sokma ====

    async def join_assistant(self, original_chat_id: int, chat_id: int):
        language = await get_lang(original_chat_id)
        _ = get_string(language)

        userbot = await get_assistant(chat_id)  # asistan profili/id
        try:
            try:
                get = await app.get_chat_member(chat_id, userbot.id)
            except ChatAdminRequired:
                raise AssistantErr(_["call_1"])  # Botu admin yapın, vb.

            if get.status in (ChatMemberStatus.BANNED, ChatMemberStatus.LEFT):
                raise AssistantErr(_["call_2"].format(userbot.username, userbot.id))

        except UserNotParticipant:
            chat = await app.get_chat(chat_id)
            if chat.username:
                try:
                    await self.userbot1.join_chat(chat.username)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise AssistantErr(_["call_3"].format(e))
            else:
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
                    await asyncio.sleep(2)
                    await self.userbot1.join_chat(invitelink)
                    await asyncio.sleep(2)
                    await m.edit(_["call_6"].format(userbot.name))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise AssistantErr(_["call_3"].format(e))

    # ==== Çağrıya katılma ====

    async def join_call(self, chat_id: int, original_chat_id: int, link: str, video: Union[bool, str] = None):
        assistant = await self._assistant_client(chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)

        stream = (
            AudioVideoPiped(link, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality)
            if video else
            AudioPiped(link, audio_parameters=audio_stream_quality)
        )

        try:
            await assistant.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        except NoActiveGroupCall:
            try:
                await self.join_assistant(original_chat_id, chat_id)
            except Exception as e:
                raise e
            try:
                await assistant.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
            except Exception:
                raise AssistantErr(
                    "**Aktif Sesli Sohbet Bulunamadı**\n\n"
                    "Lütfen grubun sesli sohbetini açın. Açık ise kapatıp yeniden başlatın; "
                    "sorun devam ederse /restart deneyin."
                )
        except AlreadyJoinedError:
            raise AssistantErr(
                "**Asistan zaten sesli sohbette**\n\n"
                "Genelde aynı anda 2 sorgu verildiğinde olur. "
                "Asistan görünmüyorsa sesli sohbeti kapatıp açın veya /restart deneyin."
            )
        except TelegramServerError:
            raise AssistantErr(
                "**Telegram Sunucu Hatası**\n\n"
                "Lütfen tekrar deneyin. Sık olursa sesli sohbeti kapatıp açın."
            )

        await add_active_chat(chat_id)
        await mute_off(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)

    # ==== Kuyruk geçişi ====

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

            if popped and config.AUTO_DOWNLOADS_CLEAR == str(True):
                try:
                    from ArchMusic.utils.stream.autoclear import auto_clean
                    await auto_clean(popped)
                except Exception:
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

        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        videoid = check[0]["vidid"]
        check[0]["played"] = 0

        def mk_stream(src, as_video: bool):
            if as_video:
                return AudioVideoPiped(src, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality)
            return AudioPiped(src, audio_parameters=audio_stream_quality)

        try:
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(original_chat_id, text=_["call_9"])
                await client.change_stream(chat_id, mk_stream(link, str(streamtype) == "video"))
                await app.send_message(
                    chat_id=original_chat_id,
                    text=_["stream_1"].format(
                        title,
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                )
                db[chat_id][0]["markup"] = "tg"

            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_10"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=True if str(streamtype) == "video" else False,
                    )
                except Exception:
                    return await mystic.edit_text(_["call_9"], disable_web_page_preview=True)

                await client.change_stream(chat_id, mk_stream(file_path, str(streamtype) == "video"))
                await mystic.delete()
                await app.send_message(
                    chat_id=original_chat_id,
                    text=_["stream_1"].format(
                        title,
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                )
                db[chat_id][0]["markup"] = "stream"

            elif "index_" in queued:
                await client.change_stream(chat_id, mk_stream(videoid, str(streamtype) == "video"))
                await app.send_message(
                    chat_id=original_chat_id,
                    text=_["stream_2"].format(
                        title,
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        check[0]["dur"],
                        user,
                    ),
                )
                db[chat_id][0]["markup"] = "tg"

            else:
                await client.change_stream(chat_id, mk_stream(queued, str(streamtype) == "video"))
                if videoid in ("telegram", "soundcloud"):
                    await app.send_message(
                        original_chat_id,
                        text=_["stream_3"].format(title, check[0]["dur"], user),
                    )
                    db[chat_id][0]["markup"] = "tg"
                else:
                    await app.send_message(
                        chat_id=original_chat_id,
                        text=_["stream_1"].format(
                            title,
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            check[0]["dur"],
                            user,
                        ),
                    )
                    db[chat_id][0]["markup"] = "stream"

        except Exception:
            return await app.send_message(original_chat_id, text=_["call_9"])

    # ==== Başlat / Durdur ====

    async def start(self):
        await self.userbot1.start()
        await self.one.start()
        LOGGER.info("Assistant client ve PyTgCalls başlatıldı (STRING1).")

    async def stop(self):
        try:
            await self.one.stop()
        finally:
            await self.userbot1.stop()
        LOGGER.info("Assistant client ve PyTgCalls durduruldu.")


# Projede beklenen isim
ArchMusic = Call()
