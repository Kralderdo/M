# -*- coding: utf-8 -*-
#
# ParsMuzikBot - Gelişmiş Play Sistemi (FULL Pro Fallback)
# Telegram Blue • TR UI • YouTube API v3 yedekli
# by @Kralderdo

import os
import re
import time
import random
import string
import requests

from typing import Optional, Tuple, List
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
    track_markup,
)
from ArchMusic.utils.inline.playlist import botplaylist_markup
from ArchMusic.utils.logger import play_logs
from ArchMusic.utils.stream.stream import stream

# =========================================================
# ✅ YouTube API Key (Kullanıcı Keyi)
# =========================================================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So"
os.environ["YOUTUBE_API_KEY"] = YOUTUBE_API_KEY

# YouTube V3 API uçları
YTV3_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YTV3_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


# =========================================================
# Yardımcılar
# =========================================================
def iso8601_to_time(duration: str) -> str:
    """PT4M13S -> 4:13"""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not m:
        return "0:00"
    h = int(m.group(1) or 0)
    mm = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    total = h * 3600 + mm * 60 + s
    mins, secs = divmod(total, 60)
    return f"{mins}:{secs:02d}"


def yt_v3_search_first(query: str) -> Optional[Tuple[dict, str]]:
    """YouTube Data API v3 ile ilk uygun sonucu döndür."""
    try:
        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 1,
            "safeSearch": "none",
        }
        sres = requests.get(YTV3_SEARCH_URL, params=params, timeout=10).json()
        if "items" not in sres or not sres["items"]:
            return None
        vid = sres["items"][0]["id"]["videoId"]
        vdet = requests.get(
            YTV3_VIDEOS_URL,
            params={"key": YOUTUBE_API_KEY, "part": "snippet,contentDetails", "id": vid},
            timeout=10,
        ).json()
        if "items" not in vdet or not vdet["items"]:
            return None
        info = vdet["items"][0]
        title = info["snippet"]["title"]
        duration = iso8601_to_time(info["contentDetails"]["duration"])
        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        return (
            {"title": title, "duration_min": duration, "thumb": thumb, "link": f"https://youtu.be/{vid}"},
            vid,
        )
    except Exception:
        return None


def yt_v3_search_alternatives(query: str, limit: int = 5) -> List[Tuple[dict, str]]:
    """YouTube Data API v3 ile alternatif sonuçlar (ilk 'limit' sonuç)."""
    out = []
    try:
        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max(1, min(limit, 10)),
            "safeSearch": "none",
        }
        sres = requests.get(YTV3_SEARCH_URL, params=params, timeout=10).json()
        for it in sres.get("items", []):
            vid = it["id"]["videoId"]
            vdet = requests.get(
                YTV3_VIDEOS_URL,
                params={"key": YOUTUBE_API_KEY, "part": "snippet,contentDetails", "id": vid},
                timeout=10,
            ).json()
            if not vdet.get("items"):
                continue
            info = vdet["items"][0]
            title = info["snippet"]["title"]
            duration = iso8601_to_time(info["contentDetails"]["duration"])
            thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
            out.append(
                ({"title": title, "duration_min": duration, "thumb": thumb, "link": f"https://youtu.be/{vid}"}, vid)
            )
    except Exception:
        pass
    return out


async def safe_pick_youtube(query_or_url: str) -> Optional[Tuple[dict, str]]:
    """
    Güvenli YouTube seçici:
    1) URL/Query -> YouTube.track
    2) V3 ilk sonuç
    3) V3 alternatiflerden sırayla dene
    """
    # 1) Doğrudan YouTube.track dene
    try:
        if query_or_url.startswith("http"):
            details, vid = await YouTube.track(query_or_url)
            return details, vid
        # query ise:
        details, vid = await YouTube.track(query_or_url)
        return details, vid
    except Exception:
        pass

    # 2) V3 ilk sonuç
    v3 = yt_v3_search_first(query_or_url)
    if v3:
        details, vid = v3
        # YouTube.track ile doğrula (stream tarafı iç uyum)
        try:
            details2, _ = await YouTube.track(details["link"])
            return details2, vid
        except Exception:
            # 3) Alternatiflere düş
            pass

    # 3) Alternatifler
    for det, vid in yt_v3_search_alternatives(query_or_url, limit=6):
        try:
            details2, _ = await YouTube.track(det["link"])
            return details2, vid
        except Exception:
            continue

    return None


# =========================================================
# SPAM KORUMA
# =========================================================
PLAY_COMMAND = get_command("PLAY_COMMAND")
spam_protection = True
spam_records = {}

@app.on_message(filters.command("spam") & filters.user(config.OWNER_ID))
async def spam_toggle(_, message: Message):
    global spam_protection
    if len(message.command) != 2:
        status = "✅ Açık" if spam_protection else "❌ Kapalı"
        return await message.reply_text(f"Spam koruması: {status}\nKullanım: `/spam on` / `/spam off`")
    arg = message.command[1].lower()
    spam_protection = (arg == "on")
    return await message.reply_text("✅ Açıldı." if spam_protection else "❌ Kapatıldı.")


# =========================================================
# /play KOMUTU (FULL Pro Fallback)
# =========================================================
@app.on_message(filters.command(PLAY_COMMAND) & filters.group & ~BANNED_USERS)
@PlayWrapper
async def play_command(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):

    # Spam
    global spam_records
    uid = message.from_user.id
    now = time.time()
    if spam_protection:
        spam_records.setdefault(uid, [])
        spam_records[uid] = [t for t in spam_records[uid] if now - t < 5]
        spam_records[uid].append(now)
        if len(spam_records[uid]) > 6:
            await message.reply_text("⛔ Spam tespit edildi. Bot bu gruptan çıkıyor.")
            try:
                await app.leave_chat(message.chat.id)
            except Exception:
                pass
            return

    mystic = await message.reply_text(_["play_1"])

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Cevaplanan medyadan çalma
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

    # =====================================================
    # 1) TELEGRAM SES
    # =====================================================
    if audio_telegram:
        if audio_telegram.file_size > config.TG_AUDIO_FILESIZE_LIMIT:
            return await mystic.edit_text("❌ Bu ses dosyası çok büyük.")
        duration_min = seconds_to_min(audio_telegram.duration)
        if audio_telegram.duration > config.DURATION_LIMIT:
            return await mystic.edit_text(
                f"⛔ En fazla {config.DURATION_LIMIT_MIN} dk çalabilirim. Bu: `{duration_min}`."
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
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")
            await mystic.delete()
            return

    # =====================================================
    # 2) TELEGRAM VİDEO
    # =====================================================
    if video_telegram:
        if not await is_video_allowed(message.chat.id):
            return await mystic.edit_text("🚫 Bu grupta video oynatma kapalı.")
        if message.reply_to_message.document and video_telegram.file_name:
            ext = (video_telegram.file_name.rsplit(".", 1)[-1] or "").lower()
            if ext not in formats:
                return await mystic.edit_text(f"❗ Desteklenmeyen format. ({' | '.join(formats)})")
        if video_telegram.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await mystic.edit_text("❌ Video boyutu çok büyük.")
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
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")
            await mystic.delete()
            return

    # =====================================================
    # 3) URL İLE (YouTube / Spotify / Apple / Resso / SC / Radyo)
    # =====================================================
    details = None
    track_id = None
    plist_type = None
    plist_id = None
    spotify_flag = False

    if url:
        # 3.a) YouTube linkleri
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, user_id)
                except Exception:
                    return await mystic.edit_text("❌ Playlist alınamadı.")
                plist_type = "yt"
                streamtype = "playlist"
                img = config.PLAYLIST_IMG_URL
                cap = "✅ YouTube Playlist bulundu."
                # list= parametresini çek
                if "list=" in url:
                    plist_id = url.split("list=")[1].split("&")[0]
                else:
                    plist_id = "yt_list"
            else:
                # Tekil video – güvenli seçim
                picked = await safe_pick_youtube(url)
                if not picked:
                    return await mystic.edit_text("❌ YouTube videosu oynatılamıyor (telif/engel).")
                details, track_id = picked
                streamtype = "youtube"
                img = details["thumb"]
                cap = f"🎧 {details['title']}"

        # 3.b) Spotify
        elif await Spotify.valid(url):
            spotify_flag = True
            if "track" in url:
                try:
                    details, track_id = await Spotify.track(url)
                except Exception:
                    # Spotify → YouTube fallback
                    q = url
                    picked = await safe_pick_youtube(q)
                    if not picked:
                        return await mystic.edit_text("❌ Spotify parçası çözülemedi.")
                    details, track_id = picked
                streamtype = "youtube"
                img = details["thumb"]
                cap = f"🎧 {details['title']}"
            elif "playlist" in url:
                plist_type = "spplay"
                try:
                    details, plist_id = await Spotify.playlist(url)
                except Exception:
                    return await mystic.edit_text("❌ Spotify playlist alınamadı.")
                streamtype = "playlist"
                img = config.SPOTIFY_PLAYLIST_IMG_URL
                cap = "🎶 Spotify Playlist"
            elif "album" in url:
                plist_type = "spalbum"
                try:
                    details, plist_id = await Spotify.album(url)
                except Exception:
                    return await mystic.edit_text("❌ Spotify albüm alınamadı.")
                streamtype = "playlist"
                img = config.SPOTIFY_ALBUM_IMG_URL
                cap = "🎶 Spotify Albüm"
            else:
                return await mystic.edit_text("❗ Spotify linki desteklenmiyor.")

        # 3.c) Apple Music
        elif await Apple.valid(url):
            try:
                details, track_id = await Apple.track(url)
            except Exception:
                return await mystic.edit_text("❌ Apple Music parçası alınamadı.")
            streamtype = "youtube"
            img = details["thumb"]
            cap = f"🍎 {details['title']}"

        # 3.d) Resso
        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
            except Exception:
                return await mystic.edit_text("❌ Resso parçası alınamadı.")
            streamtype = "youtube"
            img = details["thumb"]
            cap = f"🎵 {details['title']}"

        # 3.e) SoundCloud
        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except Exception:
                return await mystic.edit_text("❌ SoundCloud indirilemedi.")
            if details.get("duration_sec", 0) > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    f"⛔ En fazla {config.DURATION_LIMIT_MIN} dk çalabilirim."
                )
            try:
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id,
                             streamtype="soundcloud", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")
            await mystic.delete()
            return

        # 3.f) Radyo/M3U8/Index
        else:
            try:
                await ArchMusic.stream_call(url)
            except NoActiveGroupCall:
                await mystic.edit_text("❗ Sesli sohbet açık değil. Lütfen VC başlatın.")
                try:
                    await app.send_message(config.LOG_GROUP_ID, f"VC kapalı: {message.chat.title}")
                except Exception:
                    pass
                return
            except Exception as e:
                return await mystic.edit_text(f"⚠️ URL akışı hata: `{type(e).__name__}`")
            await mystic.edit_text("📡 Yayın başlatılıyor...")
            try:
                await stream(_, mystic, user_id, url, chat_id, user_name, message.chat.id,
                             video=video, streamtype="index", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")
            return await play_logs(message, streamtype="M3U8/Index")

        # URL yolunda buradaysak, buton kartını hazırla
        if streamtype == "playlist":
            # Seçim menüsü
            ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[ran_hash] = plist_id
            btns = playlist_markup(_, ran_hash, user_id, plist_type, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(btns))
            return await play_logs(message, streamtype=f"Playlist:{plist_type}")
        else:
            # Tekil parça – doğrudan/menülü
            if str(playmode) == "Direct":
                # süre kontrolü
                if details.get("duration_min"):
                    dsec = time_to_seconds(details["duration_min"])
                    if dsec and dsec > config.DURATION_LIMIT:
                        return await mystic.edit_text(
                            f"⛔ En fazla {config.DURATION_LIMIT_MIN} dk çalabilirim. ({details['duration_min']})"
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
                        video=video,
                        streamtype="youtube",
                        spotify=spotify_flag,
                        forceplay=fplay,
                    )
                except Exception as e:
                    return await mystic.edit_text(f"⚠️ Akış hatası: `{type(e).__name__}`")
                await mystic.delete()
                return await play_logs(message, streamtype="youtube")

            # menülü
            btns = track_markup(_, track_id, user_id, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            return await message.reply_photo(photo=details["thumb"], caption=cap, reply_markup=InlineKeyboardMarkup(btns))

    # =====================================================
    # 4) /play + ARAMA METNİ
    # =====================================================
    if len(message.command) < 2:
        buttons = botplaylist_markup(_)
        return await mystic.edit_text(_["playlist_1"], reply_markup=InlineKeyboardMarkup(buttons))

    query = message.text.split(None, 1)[1]
    if "-v" in query:
        video = True
        query = query.replace("-v", "").strip()

    # Güvenli YouTube seçimi
    picked = await safe_pick_youtube(query)
    if not picked:
        return await mystic.edit_text("❌ Sonuç bulunamadı veya video engelli.")
    details, track_id = picked

    # Direct mod
    if str(playmode) == "Direct":
        if details.get("duration_min"):
            dsec = time_to_seconds(details["duration_min"])
            if dsec and dsec > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    f"⛔ En fazla {config.DURATION_LIMIT_MIN} dk çalabilirim. ({details['duration_min']})"
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
                video=video,
                streamtype="youtube",
                forceplay=fplay,
            )
        except Exception as e:
            return await mystic.edit_text(f"⚠️ Akış hatası: `{type(e).__name__}`")
        await mystic.delete()
        return await play_logs(message, streamtype="youtube")

    # Menülü kart
    btns = track_markup(_, track_id, user_id, "c" if channel else "g", "f" if fplay else "d")
    await mystic.delete()
    return await message.reply_photo(
        photo=details["thumb"],
        caption=f"🎶 {details['title']}",
        reply_markup=InlineKeyboardMarkup(btns),
    )


print("[ParsMuzikBot] ✅ play.py (FULL Pro Fallback) yüklendi!")
