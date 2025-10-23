# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 by ArchBots
# GNU v3.0 License
#
# File: plugins/play/play.py
#
# Not: Bu dosya, kullanıcı isteğiyle YouTube API KEY DOĞRUDAN koda gömülecek
# şekilde düzenlenmiştir. Public client key yerine aşağıdaki KEY kullanılacaktır.

import os
import re
import time
import random
import string
import json
from typing import Optional, Tuple

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS, lyrical
from strings import get_command
from ArchMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils import seconds_to_min, time_to_seconds
from ArchMusic.utils.channelplay import get_channeplayCB
from ArchMusic.utils.database import is_video_allowed
from ArchMusic.utils.decorators.language import languageCB
from ArchMusic.utils.decorators.play import PlayWrapper
from ArchMusic.utils.formatters import formats
from ArchMusic.utils.inline.play import (
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from ArchMusic.utils.inline.playlist import botplaylist_markup
from ArchMusic.utils.logger import play_logs
from ArchMusic.utils.stream.stream import stream

# ============================================================
# 🔑 YouTube API Key (KODA GÖMÜLÜ) — Kullanıcının verdiği KEY
# ============================================================
YOUTUBE_API_KEY = "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So"

# Çevre değişkenine ve olası YouTube helper'a enjekte etmeyi dene
try:
    os.environ["YOUTUBE_API_KEY"] = YOUTUBE_API_KEY
except Exception:
    pass

try:
    # Bazı fork'larda YouTube helper içinde API_KEY alanı bulunuyor
    setattr(YouTube, "API_KEY", YOUTUBE_API_KEY)
except Exception:
    pass

# ------------------------------------------------------------
# Fallback YouTube Data API v3 araması (requests gerekir)
# ------------------------------------------------------------
# Not: Projede 'requests' çoğunlukla requirements'ta var. Yoksa ekleyin.
import requests

YTV3_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YTV3_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def iso8601_duration_to_mmss(iso: str) -> str:
    # Örn: PT3M15S -> 3:15
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not match:
        return ""
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    total = h * 3600 + m * 60 + s
    mm = total // 60
    ss = total % 60
    return f"{mm}:{ss:02d}"


def ytapi_search_first(query: str) -> Optional[Tuple[dict, str]]:
    """
    YouTube Data API v3 ile ilk uygun sonucu döndürür.
    Return: (details, track_id) veya None
    details: {"title", "duration_min", "thumb", "link"}
    """
    try:
        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "type": "video",
            "maxResults": 1,
            "q": query.strip(),
            "safeSearch": "none",
        }
        r = requests.get(YTV3_SEARCH_URL, params=params, timeout=10)
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            return None
        vid = items[0]["id"]["videoId"]
        # Videonun süresi/thumbnail'i için videos endpoint
        vparams = {
            "key": YOUTUBE_API_KEY,
            "part": "contentDetails,snippet",
            "id": vid,
        }
        v = requests.get(YTV3_VIDEOS_URL, params=vparams, timeout=10)
        v.raise_for_status()
        vitems = v.json().get("items", [])
        if not vitems:
            return None
        snip = vitems[0]["snippet"]
        cdet = vitems[0]["contentDetails"]
        title = snip.get("title") or "YouTube"
        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        dur_iso = cdet.get("duration") or ""
        duration_min = iso8601_duration_to_mmss(dur_iso)  # "mm:ss"
        link = f"https://www.youtube.com/watch?v={vid}"
        details = {
            "title": title,
            "duration_min": duration_min,
            "thumb": thumb,
            "link": link,
        }
        return details, vid
    except Exception:
        return None


# Komut: /play
PLAY_COMMAND = get_command("PLAY_COMMAND")

# Basit spam koruması
spam_protection = True
spam_records = {}


@app.on_message(filters.command("spam") & filters.user(config.OWNER_ID))
async def spam_toggle(client, message: Message):
    global spam_protection
    if len(message.command) != 2:
        status = "Açık ✅" if spam_protection else "Kapalı ❌"
        return await message.reply_text(f"**Mevcut Durum:** {status}\n\n**Kullanım:** `/spam [on/off]`")

    param = message.command[1].lower()
    if param == "on":
        if spam_protection:
            return await message.reply_text("**Spam koruması zaten açık.** ✅")
        spam_protection = True
        await message.reply_text("**Spam koruması etkinleştirildi. 🟢**")
    elif param == "off":
        if not spam_protection:
            return await message.reply_text("**Spam koruması zaten kapalı.** ❌")
        spam_protection = False
        await message.reply_text("**Spam koruması devre dışı bırakıldı. 🔴**")
    else:
        await message.reply_text("**Geçersiz parametre. Kullanım:** `/spam [on/off]`")


@app.on_message(
    filters.command(PLAY_COMMAND)
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_command(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    global spam_records

    # Basit spam kontrolü
    if spam_protection:
        user_id = message.from_user.id
        current_time = time.time()
        rec = spam_records.get(user_id, [])
        rec.append(current_time)
        # Son 5 sn içindeki istekleri tut
        rec = [t for t in rec if current_time - t <= 5]
        spam_records[user_id] = rec
        if len(rec) >= 5:
            await message.reply_text(
                f"**{message.from_user.mention} spam tespit edildi!** 🚨\n\n**Bot gruptan ayrılıyor...**"
            )
            chat = message.chat
            group_link = f"@{chat.username}" if chat.username else "Gizli"
            await app.send_message(
                config.LOG_GROUP_ID,
                (
                    "🚨 **__SPAM ALGILANDI__** 🚨\n\n"
                    f"👤 **Kullanıcı:** {message.from_user.mention} [`{message.from_user.id}`]\n"
                    f"📌 **Grup:** {message.chat.title}\n"
                    f"🆔 **Grup ID:** `{message.chat.id}`\n"
                    f"🔗 **Grup Linki:** {group_link}\n"
                    f"💬 **Spam Mesajı:** {message.text}\n\n"
                    "**Durum:** Bot, spam nedeniyle bu gruptan ayrıldı."
                ),
            )
            return await app.leave_chat(message.chat.id)

    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    plist_id = None
    slider = None
    plist_type = None
    spotify = None
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Cevaplanan mesajdan medya yakala
    audio_telegram = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    video_telegram = (
        (message.reply_to_message.video or message.reply_to_message.document)
        if message.reply_to_message
        else None
    )

    # --- Telegram AUDIO ---
    if audio_telegram:
        if audio_telegram.file_size > config.TG_AUDIO_FILESIZE_LIMIT:
            return await mystic.edit_text(_["play_5"])
        duration_min = seconds_to_min(audio_telegram.duration)
        if (audio_telegram.duration) > config.DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, duration_min)
            )
        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(audio_telegram, audio=True)
            dur = await Telegram.get_duration(audio_telegram)
            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": dur,
            }
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="telegram",
                    forceplay=fplay,
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
                return await mystic.edit_text(err)
            return await mystic.delete()
        return

    # --- Telegram VIDEO ---
    elif video_telegram:
        if not await is_video_allowed(message.chat.id):
            return await mystic.edit_text(_["play_3"])
        if message.reply_to_message.document:
            try:
                ext = video_telegram.file_name.split(".")[-1]
                if ext.lower() not in formats:
                    return await mystic.edit_text(
                        _["play_8"].format(f"{' | '.join(formats)}")
                    )
            except Exception:
                return await mystic.edit_text(_["play_8"].format(f"{' | '.join(formats)}"))
        if video_telegram.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await mystic.edit_text(_["play_9"])

        file_path = await Telegram.get_filepath(video=video_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(video_telegram)
            dur = await Telegram.get_duration(video_telegram)
            details = {"title": file_name, "link": message_link, "path": file_path, "dur": dur}
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    video=True,
                    streamtype="telegram",
                    forceplay=fplay,
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
                return await mystic.edit_text(err)
            return await mystic.delete()
        return

    # --- URL İŞLEME ---
    elif url:
        if await YouTube.exists(url):
            # YouTube URL
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
                except Exception as e:
                    print(e)
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "yt"
                if "&" in url:
                    plist_id = (url.split("=")[1]).split("&")[0]
                else:
                    plist_id = url.split("=")[1]
                img = config.PLAYLIST_IMG_URL
                cap = _["play_10"]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except Exception as e:
                    # Fallback: Data API ile id'yi kullan
                    try:
                        vid = url.split("v=")[-1].split("&")[0]
                    except Exception:
                        vid = None
                    if not vid:
                        return await mystic.edit_text(_["play_3"])
                    vparams = {
                        "key": YOUTUBE_API_KEY,
                        "part": "contentDetails,snippet",
                        "id": vid,
                    }
                    v = requests.get(YTV3_VIDEOS_URL, params=vparams, timeout=10).json()
                    items = v.get("items", [])
                    if not items:
                        return await mystic.edit_text(_["play_3"])
                    snip = items[0]["snippet"]
                    cdet = items[0]["contentDetails"]
                    details = {
                        "title": snip.get("title") or "YouTube",
                        "duration_min": iso8601_duration_to_mmss(cdet.get("duration") or ""),
                        "thumb": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                        "link": f"https://www.youtube.com/watch?v={vid}",
                    }
                    track_id = vid
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])

        elif await Spotify.valid(url):
            spotify = True
            if (not config.SPOTIFY_CLIENT_ID) and (not config.SPOTIFY_CLIENT_SECRET):
                return await mystic.edit_text(
                    "Bu bot Spotify sorgularını oynatamıyor. Lütfen sahibimden Spotify'ı etkinleştirmesini isteyin."
                )
            if "track" in url:
                try:
                    details, track_id = await Spotify.track(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
            elif "playlist" in url:
                try:
                    details, plist_id = await Spotify.playlist(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "spplay"
                img = config.SPOTIFY_PLAYLIST_IMG_URL
                cap = _["play_12"].format(message.from_user.first_name)
            elif "album" in url:
                try:
                    details, plist_id = await Spotify.album(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "spalbum"
                img = config.SPOTIFY_ALBUM_IMG_URL
                cap = _["play_12"].format(message.from_user.first_name)
            elif "artist" in url:
                try:
                    details, plist_id = await Spotify.artist(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "spartist"
                img = config.SPOTIFY_ARTIST_IMG_URL
                cap = _["play_12"].format(message.from_user.first_name)
            else:
                return await mystic.edit_text(_["play_17"])

        elif await Apple.valid(url):
            if "album" in url or "track" in url:
                try:
                    details, track_id = await Apple.track(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
            elif "playlist" in url:
                spotify = True
                try:
                    details, plist_id = await Apple.playlist(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "apple"
                cap = _["play_13"].format(message.from_user.first_name)
                img = url
            else:
                return await mystic.edit_text(_["play_16"])

        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
            except Exception:
                return await mystic.edit_text(_["play_3"])
            streamtype = "youtube"
            img = details["thumb"]
            cap = _["play_11"].format(details["title"], details["duration_min"])

        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except Exception:
                return await mystic.edit_text(_["play_3"])
            duration_sec = details["duration_sec"]
            if duration_sec > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    _["play_6"].format(config.DURATION_LIMIT_MIN, details["duration_min"])
                )
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="soundcloud",
                    forceplay=fplay,
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
                return await mystic.edit_text(err)
            return await mystic.delete()

        else:
            # M3U8/INDEX link stream
            try:
                await ArchMusic.stream_call(url)
            except NoActiveGroupCall:
                await mystic.edit_text(
                    "Botta bir sorun var. Lütfen sahibime bildirin ve kayıt grubunu kontrol etmelerini isteyin."
                )
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    "Lütfen Sesli Sohbeti açın.. Bot URL'leri aktaramıyor..",
                )
            except Exception as e:
                return await mystic.edit_text(_["general_3"].format(type(e).__name__))
            await mystic.edit_text(_["str_2"])
            try:
                await stream(
                    _,
                    mystic,
                    message.from_user.id,
                    url,
                    chat_id,
                    message.from_user.first_name,
                    message.chat.id,
                    video=video,
                    streamtype="index",
                    forceplay=fplay,
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
                return await mystic.edit_text(err)
            return await play_logs(message, streamtype="M3u8 or Index Link")

    # --- Query ile arama (/play şarkı adı) ---
    else:
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await mystic.edit_text(_["playlist_1"], reply_markup=InlineKeyboardMarkup(buttons))
        slider = True
        query = message.text.split(None, 1)[1]
        if "-v" in query:
            query = query.replace("-v", "")

        # Önce mevcut YouTube helper ile dene
        try:
            details, track_id = await YouTube.track(query)
        except Exception:
            # Fallback: Data API v3 kullan
            res = ytapi_search_first(query)
            if not res:
                return await mystic.edit_text(_["play_3"])
            details, track_id = res
        streamtype = "youtube"

    # ======== Direct / Select (slider) kontrolü ========
    if str(playmode) == "Direct":
        if not plist_type:
            
