# -*- coding: utf-8 -*-
#
# ParsMuzikBot - Gelişmiş Play Sistemi (YouTube API Entegre)
# Düzenleme: @Kralderdo
# Tam Entegre Çalışır Sistem ✔
# ----------------------------------------------

import os
import re
import time
import random
import string
import requests

from typing import Optional, Tuple
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message
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
    track_markup
)
from ArchMusic.utils.inline.playlist import botplaylist_markup
from ArchMusic.utils.logger import play_logs
from ArchMusic.utils.stream.stream import stream

# =========================================================
# ✅ YouTube API Key (Kullanıcı Keyi ile çalışır)
# =========================================================
YOUTUBE_API_KEY = "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So"
os.environ["YOUTUBE_API_KEY"] = YOUTUBE_API_KEY

# =========================================================
# YouTube V3 API Fallback (Arama)
# =========================================================
YTV3_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YTV3_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

def iso8601_to_time(duration):
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return "0:00"
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    total = h * 3600 + m * 60 + s
    mins, secs = divmod(total, 60)
    return f"{mins}:{secs:02d}"

def youtube_api_search(query: str) -> Optional[Tuple[dict, str]]:
    try:
        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 1,
            "safeSearch": "none",
        }
        res = requests.get(YTV3_SEARCH_URL, params=params).json()
        if "items" not in res or not res["items"]:
            return None
        vid = res["items"][0]["id"]["videoId"]
        details = requests.get(
            YTV3_VIDEOS_URL,
            params={"key": YOUTUBE_API_KEY, "part": "snippet,contentDetails", "id": vid}
        ).json()
        info = details["items"][0]
        title = info["snippet"]["title"]
        duration = iso8601_to_time(info["contentDetails"]["duration"])
        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        return (
            {"title": title, "duration_min": duration, "thumb": thumb, "link": f"https://youtu.be/{vid}"},
            vid,
        )
    except Exception:
        return None

# =========================================================
# ✅ SPAM KORUMA SİSTEMİ
# =========================================================
PLAY_COMMAND = get_command("PLAY_COMMAND")
spam_protection = True
spam_records = {}

@app.on_message(filters.command("spam") & filters.user(config.OWNER_ID))
async def spam_toggle(_, message: Message):
    global spam_protection
    if len(message.command) != 2:
        status = "✅ Açık" if spam_protection else "❌ Kapalı"
        return await message.reply_text(f"Spam koruması şu an: {status}\n\nKullanım: `/spam on` veya `/spam off`")

    mode = message.command[1].lower()
    if mode == "on":
        spam_protection = True
        return await message.reply_text("✅ Spam koruması açıldı.")
    elif mode == "off":
        spam_protection = False
        return await message.reply_text("✅ Spam koruması kapatıldı.")
    else:
        return await message.reply_text("⚠️ Geçersiz seçenek! `/spam on` veya `/spam off` kullan.")

# =========================================================
# ✅ PLAY KOMUTU
# =========================================================
@app.on_message(filters.command(PLAY_COMMAND) & filters.group & ~BANNED_USERS)
@PlayWrapper
async def play_command(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):

    global spam_records
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Spam koruması
    if spam_protection:
        now = time.time()
        if user_id in spam_records:
            spam_records[user_id] = [ts for ts in spam_records[user_id] if now - ts < 5]
            spam_records[user_id].append(now)
            if len(spam_records[user_id]) > 5:
                await message.reply_text("⛔ Spam tespit edildi! Bot bu gruptan çıkıyor.")
                await app.leave_chat(message.chat.id)
                return
        else:
            spam_records[user_id] = [now]

    mystic = await message.reply_text(_["play_1"])

# 🎧 Cevaplanmış mesajdan medya kontrolü (ses/video)
    audio_telegram = (
        message.reply_to_message.audio
        if message.reply_to_message and message.reply_to_message.audio
        else message.reply_to_message.voice
        if message.reply_to_message and message.reply_to_message.voice
        else None
    )

    video_telegram = (
        message.reply_to_message.video
        if message.reply_to_message and message.reply_to_message.video
        else message.reply_to_message.document
        if message.reply_to_message and message.reply_to_message.document
        else None
    )

    # =========================================================
    # ✅ Telegram SES dosyasından oynatma
    # =========================================================
    if audio_telegram:
        if audio_telegram.file_size > config.TG_AUDIO_FILESIZE_LIMIT:
            return await mystic.edit_text("❌ Bu ses dosyası çok büyük, işlenemiyor.")

        duration_min = seconds_to_min(audio_telegram.duration)
        if audio_telegram.duration > config.DURATION_LIMIT:
            return await mystic.edit_text(
                f"⛔ Maksimum {config.DURATION_LIMIT_MIN} dakika çalabilirim.\n"
                f"Bu dosya: `{duration_min}` dakika."
            )

        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            details = {
                "title": await Telegram.get_filename(audio_telegram, audio=True),
                "link": await Telegram.get_link(message),
                "path": file_path,
                "dur": await Telegram.get_duration(audio_telegram),
            }
            try:
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id,
                             streamtype="telegram", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(f"⚠️ Hata: {type(e).__name__}")
            return await mystic.delete()
        return

    # =========================================================
    # ✅ Telegram VİDEO dosyasından oynatma
    # =========================================================
    elif video_telegram:
        if not await is_video_allowed(message.chat.id):
            return await mystic.edit_text("🚫 Bu grupta video çalma devre dışı.")

        if video_telegram.file_name:
            ext = video_telegram.file_name.split(".")[-1].lower()
            if ext not in formats:
                return await mystic.edit_text(f"❗ Desteklenmeyen video formatı: `{ext}`")

        if video_telegram.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await mystic.edit_text("❌ Video boyutu çok büyük, işlenemiyor.")

        file_path = await Telegram.get_filepath(video=video_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            details = {
                "title": await Telegram.get_filename(video_telegram),
                "link": await Telegram.get_link(message),
                "path": file_path,
                "dur": await Telegram.get_duration(video_telegram),
            }
            try:
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id,
                             video=True, streamtype="telegram", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(f"⚠️ Hata: {type(e).__name__}")
            return await mystic.delete()
        return

# =========================================================
    # ✅ URL – YouTube / Spotify / Apple / SoundCloud / Resso
    # =========================================================
    elif url:
        plist_type = None
        spotify = False

        # ✅ YouTube URL desteği
        if await YouTube.exists(url):
            if "playlist" in url:
                details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, user_id)
                plist_type = "yt"
                img = config.PLAYLIST_IMG_URL
                cap = "✅ YouTube playlist bulundu!"
                plist_id = url.split("list=")[1].split("&")[0]
                streamtype = "playlist"
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except:
                    search = youtube_api_search(url)
                    if not search:
                        return await mystic.edit_text("❌ YouTube'da sonuç bulunamadı!")
                    details, track_id = search
                img = details["thumb"]
                cap = f"🎧 {details['title']}"
                streamtype = "youtube"

        # ✅ Spotify desteği
        elif await Spotify.valid(url):
            spotify = True
            if "track" in url:
                details, track_id = await Spotify.track(url)
                img = details["thumb"]
                cap = f"🎧 {details['title']}"
                streamtype = "youtube"
            elif "playlist" in url:
                plist_type = "spplay"
                details, plist_id = await Spotify.playlist(url)
                img = config.SPOTIFY_PLAYLIST_IMG_URL
                cap = "🎶 Spotify Playlist"
                streamtype = "playlist"
            elif "album" in url:
                plist_type = "spalbum"
                details, plist_id = await Spotify.album(url)
                img = config.SPOTIFY_ALBUM_IMG_URL
                cap = "🎶 Spotify Albüm"
                streamtype = "playlist"

        # ✅ Apple Music desteği
        elif await Apple.valid(url):
            details, track_id = await Apple.track(url)
            img = details["thumb"]
            cap = f"🍎 {details['title']}"
            streamtype = "youtube"

        # ✅ Resso desteği
        elif await Resso.valid(url):
            details, track_id = await Resso.track(url)
            img = details["thumb"]
            cap = f"🎵 {details['title']}"
            streamtype = "youtube"

        # ✅ SoundCloud desteği
        elif await SoundCloud.valid(url):
            details, track_path = await SoundCloud.download(url)
            streamtype = "soundcloud"
            img = config.SOUNCLOUD_IMG_URL
            cap = f"🎶 SoundCloud: {details['title']}"

        # ✅ Diğer URL – Canlı yayın (Radyo)
        else:
            await ArchMusic.stream_call(url)
            return await mystic.edit_text("📡 Canlı yayın başlatıldı!")

        await mystic.edit_text(cap)

    # =========================================================
    # ✅ /play komutu – Arama ile müzik çalma
    # =========================================================
    else:
        query = message.text.split(None, 1)[1]
        try:
            details, track_id = await YouTube.track(query)
        except:
            result = youtube_api_search(query)
            if not result:
                return await mystic.edit_text("❌ Şarkı bulunamadı!")
            details, track_id = result

        img = details["thumb"]
        cap = f"🎶 {details['title']}"
        streamtype = "youtube"

    # =========================================================
    # ✅ Çalma İşlemini Başlat
    # =========================================================
    buttons = track_markup(_, track_id, user_id, "c" if channel else "g", "d")
    await mystic.delete()
    return await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))


print("[ParsMuzikBot] ✅ play.py başarıyla yüklendi!")
        
