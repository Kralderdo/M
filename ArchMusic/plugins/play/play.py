# -*- coding: utf-8 -*-
#
# ParsMuzikBot - Play System
# Düzenlendi: YouTube API Key Entegre Edildi
# Telegram: @Kralderdo

import os
import re
import time
import random
import string
import requests

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

# ==========================================
# ✅ YouTube API KEY – Kullanıcı tarafından sağlanan key
# ==========================================
YOUTUBE_API_KEY = "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So"
os.environ["YOUTUBE_API_KEY"] = YOUTUBE_API_KEY

# ==========================================
# YouTube API Fallback Search (YouTube Data API v3)
# ==========================================
YTV3_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YTV3_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

def iso8601_to_time(duration):
    """PT4M13S -> 4:13"""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return "0:00"
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    total = h * 3600 + m * 60 + s
    minutes, seconds = divmod(total, 60)
    return f"{minutes}:{seconds:02d}"

def youtube_api_search(query: str) -> Optional[Tuple[dict, str]]:
    """Fallback: YouTube API Key ile direkt arama"""
    try:
        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 1,
            "safeSearch": "none",
        }
        response = requests.get(YTV3_SEARCH_URL, params=params)
        data = response.json()
        if "items" not in data or not data["items"]:
            return None

        vid = data["items"][0]["id"]["videoId"]
        # Video bilgilerini çek
        vdetails = requests.get(
            YTV3_VIDEOS_URL,
            params={"key": YOUTUBE_API_KEY, "part": "contentDetails,snippet", "id": vid},
        ).json()

        if "items" not in vdetails or not vdetails["items"]:
            return None

        info = vdetails["items"][0]
        title = info["snippet"]["title"]
        duration = iso8601_to_time(info["contentDetails"]["duration"])
        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        link = f"https://www.youtube.com/watch?v={vid}"

        return (
            {
                "title": title,
                "duration_min": duration,
                "thumb": thumb,
                "link": link,
            },
            vid,
        )
    except Exception:
        return None

# ==========================================
# Spam protection system
# ==========================================
PLAY_COMMAND = get_command("PLAY_COMMAND")
spam_protection = True
spam_records = {}

@app.on_message(filters.command("spam") & filters.user(config.OWNER_ID))
async def spam_toggle(_, message: Message):
    global spam_protection
    if len(message.command) != 2:
        status = "✅ Açık" if spam_protection else "❌ Kapalı"
        return await message.reply_text(f"**Spam koruması durumu:** {status}\n\n**Kullanım:** `/spam on` veya `/spam off`")

    mode = message.command[1].lower()
    if mode == "on":
        spam_protection = True
        return await message.reply_text("✅ Spam koruması açıldı!")
    elif mode == "off":
        spam_protection = False
        return await message.reply_text("❌ Spam koruması kapatıldı!")
    else:
        return await message.reply_text("Geçersiz komut. Kullanım: `/spam on/off`")

# ==========================================
# /play ana komutu
# ==========================================
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

    # 🚫 Spam kontrolü
    if spam_protection:
        user_id = message.from_user.id
        now = time.time()
        if user_id in spam_records:
            spam_records[user_id] = [
                t for t in spam_records[user_id] if now - t < 5
            ]
            spam_records[user_id].append(now)
            if len(spam_records[user_id]) > 5:
                await message.reply_text("🚨 Spam tespit edildi! Bot gruptan çıkıyor...")
                await app.leave_chat(message.chat.id)
                return
        else:
            spam_records[user_id] = [now]

    mystic = await message.reply_text(_["play_1"])
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Cevaplanmış mesajdan medya kontrolü
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

# Telegram ses dosyasından çalma
    if audio_telegram:
        if audio_telegram.file_size > config.TG_AUDIO_FILESIZE_LIMIT:
            return await mystic.edit_text("❌ Bu ses dosyası çok büyük, işlenemiyor.")

        duration_min = seconds_to_min(audio_telegram.duration)
        if audio_telegram.duration > config.DURATION_LIMIT:
            return await mystic.edit_text(
                f"⛔ Maksimum {config.DURATION_LIMIT_MIN} dakika uzunluğunda ses çalabilirim.\n"
                f"Bu dosya: `{duration_min}` dakika."
            )

        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(audio_telegram, audio=True)
            duration = await Telegram.get_duration(audio_telegram)

            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": duration,
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
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")
            return await mystic.delete()
        return

# Telegram video dosyasından çalma
    elif video_telegram:
        if not await is_video_allowed(message.chat.id):
            return await mystic.edit_text("🚫 Bu grupta video oynatma kapalı!")

        if message.reply_to_message.document:
            try:
                ext = video_telegram.file_name.split(".")[-1]
                if ext.lower() not in formats:
                    return await mystic.edit_text(
                        f"❗ Geçersiz video formatı!\n\nDesteklenen formatlar: `{', '.join(formats)}`"
                    )
            except:
                return await mystic.edit_text(
                    f"❗ Geçersiz video formatı!\n\nDesteklenen formatlar: `{', '.join(formats)}`"
                )

        if video_telegram.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await mystic.edit_text("❌ Bu video çok büyük, işlenemiyor.")

        file_path = await Telegram.get_filepath(video=video_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(video_telegram)
            duration = await Telegram.get_duration(video_telegram)

            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": duration,
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
                    video=True,
                    streamtype="telegram",
                    forceplay=fplay,
                )
            except Exception as e:
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")

            return await mystic.delete()
        return

# URL ile müzik oynatma (YouTube, Spotify, vs.)
    elif url:
        # YouTube linki ise
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
                except Exception as e:
                    print(e)
                    return await mystic.edit_text("❌ Playlist alınamadı!")

                plist_type = "yt"
                streamtype = "playlist"
                img = config.PLAYLIST_IMG_URL
                cap = "✅ Playlist bulundu!"
                if "&" in url:
                    plist_id = url.split("list=")[1].split("&")[0]
                else:
                    plist_id = url.split("list=")[1]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except:
                    # Eğer normal modül çözemezse API fallback başlasın
                    vid_id = url.split("watch?v=")[-1][:11]
                    yt_result = youtube_api_search(vid_id)
                    if yt_result:
                        details, track_id = yt_result
                    else:
                        return await mystic.edit_text("❌ YouTube videosu bulunamadı!")
                streamtype = "youtube"
                img = details["thumb"]
                cap = f"🎵 {details['title']}"

        # Spotify linki ise
        elif await Spotify.valid(url):
            spotify = True
            if not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
                return await mystic.edit_text("⚠️ Spotify API ayarlanmadığı için işlem yapılamıyor.")

            if "track" in url:
                details, track_id = await Spotify.track(url)
                img = details["thumb"]
                cap = f"🎵 {details['title']}"
                streamtype = "youtube"
            elif "playlist" in url:
                plist_type = "spplay"
                details, plist_id = await Spotify.playlist(url)
                img = config.SPOTIFY_PLAYLIST_IMG_URL
                cap = "🎶 Spotify playlist bulundu!"
                streamtype = "playlist"
            elif "album" in url:
                plist_type = "spalbum"
                details, plist_id = await Spotify.album(url)
                img = config.SPOTIFY_ALBUM_IMG_URL
                cap = "🎶 Spotify albüm bulundu!"
                streamtype = "playlist"
            else:
                return await mystic.edit_text("❗ Spotify linkini çözemedim.")

# Apple Music linki ise
        elif await Apple.valid(url):
            if "track" in url or "album" in url:
                try:
                    details, track_id = await Apple.track(url)
                except:
                    return await mystic.edit_text("❌ Apple Music parçası alınamadı!")
                img = details["thumb"]
                cap = f"🍎 {details['title']}"
                streamtype = "youtube"
            elif "playlist" in url:
                try:
                    details, plist_id = await Apple.playlist(url)
                except:
                    return await mystic.edit_text("❌ Apple playlist alınamadı!")
                plist_type = "apple"
                img = url
                cap = "🍎 Apple playlist bulundu!"
                streamtype = "playlist"
            else:
                return await mystic.edit_text("❗ Apple Music linki çözülemedi.")

        # Resso linki ise
        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
            except:
                return await mystic.edit_text("❌ Resso müzik bulunamadı!")
            img = details["thumb"]
            cap = f"🎵 {details['title']}"
            streamtype = "youtube"

        # SoundCloud linki ise
        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except:
                return await mystic.edit_text("❌ SoundCloud indirme hatası!")

            duration_sec = details["duration_sec"]
            if duration_sec > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    f"⛔ {config.DURATION_LIMIT_MIN} dakikadan uzun parçaları çalamam."
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
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")
            return await mystic.delete()

# Direkt URL veya Radyo/M3U8 linkleri
        else:
            try:
                await ArchMusic.stream_call(url)
            except NoActiveGroupCall:
                await mystic.edit_text(
                    "❗ Sesli sohbet açık değil!\nLütfen sesli sohbeti başlatın sonra tekrar deneyin."
                )
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"⚠️ Grup: {message.chat.title}\n➡️ Sesli sohbet kapalı olduğu için radyo bağlantısı oynatılamadı."
                )
            except Exception as e:
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")

            await mystic.edit_text("📡 Yayın işleniyor...")
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
                return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")
            return await play_logs(message, streamtype="M3U8/Index Stream")

else:
        # Kullanıcı sadece /play yazdıysa playlist menüsü aç
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await mystic.edit_text(
                _["playlist_1"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )

        # 🎯 YouTube arama modu (/play şarkı ismi)
        query = message.text.split(None, 1)[1]

        # Video modu için -v desteği
        if "-v" in query:
            video = True
            query = query.replace("-v", "").strip()

        # ✅ Önce YouTube’dan normal arama dene
        try:
            details, track_id = await YouTube.track(query)
        except:
            # ✅ Eğer normal YouTube modülü bulamazsa Fallback başlasın
            result = youtube_api_search(query)
            if not result:
                return await mystic.edit_text("❌ Şarkı bulunamadı!")
            details, track_id = result

        streamtype = "youtube"
        img = details["thumb"]
        cap = f"🎵 {details['title']}"

# ✅ Eğer direk çalma modu seçilmişse (/play şarkı)
    if str(playmode) == "Direct":
        if not plist_type:
            # Maksimum süre kontrolü
            if details.get("duration_min"):
                dur_seconds = time_to_seconds(details["duration_min"])
                if dur_seconds > config.DURATION_LIMIT:
                    return await mystic.edit_text(
                        f"⛔ Maksimum {config.DURATION_LIMIT_MIN} dakika uzunluğunda çalabilirim.\n"
                        f"Bu: `{details['duration_min']}` dakika."
                    )
            else:
                # Canlı yayın akış desteği
                buttons = livestream_markup(
                    _,
                    track_id,
                    user_id,
                    "v" if video else "a",
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                return await mystic.edit_text(
                    "🔴 Canlı yayın bulundu, seçmek için butonları kullan:",
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        # ✅ Çalmayı başlat
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
                streamtype=streamtype,
                spotify=spotify,
                forceplay=fplay,
            )
        except Exception as e:
            return await mystic.edit_text(f"⚠️ Hata: `{type(e).__name__}`")

        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)


# ✅ Eğer Direct mode değilse butonlu seçim sistemi aktifleşir
    else:
        # Playlist seçimi
        if plist_type:
            random_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[random_hash] = plist_id

            buttons = playlist_markup(
                _,
                random_hash,
                message.from_user.id,
                plist_type,
                "c" if channel else "g",
                "f" if fplay else "d",
            )

            await mystic.delete()
            await message.reply_photo(
                photo=img,
                caption=cap,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return await play_logs(message, streamtype=f"Playlist: {plist_type}")

        # Slider modu (çoklu sonuç arama)
        else:
            if "slider" in locals() or True:
                buttons = slider_markup(
                    _,
                    track_id,
                    message.from_user.id,
                    query,
                    0,
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                await mystic.delete()
                return await message.reply_photo(
                    photo=img,
                    caption=f"🎶 `{details['title']}`\n┗ 🕘 Süre: `{details['duration_min']}`",
                    reply_markup=InlineKeyboardMarkup(buttons),
        )

##########################
# HATA LOG ve KAPANIŞ
##########################

        # Aksi halde direkt butonlu parça gönder
        buttons = track_markup(
            _,
            track_id,
            message.from_user.id,
            "c" if channel else "g",
            "f" if fplay else "d",
        )
        await mystic.delete()
        return await message.reply_photo(
            photo=img,
            caption=f"🎧 `{details['title']}`\n🕘 Süre: `{details['duration_min']}`",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


# ✅ Modül yüklenirken hata olmasın diye log basalım
print("[play.py] ✅ YouTube API Key ile geliştirilmiş çalma sistemi yüklendi!")
