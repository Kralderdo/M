# -*- coding: utf-8 -*-
import os
import re
import sys
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# =========================
# Telegram API
# =========================
API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")

# Bot Token
BOT_TOKEN = getenv("BOT_TOKEN", "")

# MongoDB
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

# =========================
# Bot Zaman Limitleri
# =========================
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "180"))          # Dakika
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))

# =========================
# Sahip ve Log Grubu
# =========================
# OWNER_ID: env boş ise senin verdiğin 8481614862 varsayılan alınır
OWNER_ID = list(map(int, getenv("OWNER_ID", "8481614862").split()))
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "0"))

# =========================
# Bot Adı (ASCII olmalı!)
# =========================
# DİKKAT: ArchMusic ASCII kontrolü yapıyor. Türkçe karakter koymayalım.
MUSIC_BOT_NAME = getenv("MUSIC_BOT_NAME", "ParsMuzikBot")

# =========================
# Heroku
# =========================
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")

# =========================
# Upstream / Repo
# =========================
# Güncelleme repo’su ve dalı
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/Kralderdo/M")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
# Özel repo güncellemesi için token (opsiyonel)
GIT_TOKEN = getenv("GIT_TOKEN", "")

# Bu proje bilgisi/başlangıç menüsü için kullanılıyor
GITHUB_REPO = "https://github.com/Kralderdo/M"

# =========================
# Destek Linkleri
# =========================
# Kanal istemedin: boş bırakıyoruz (boş string sorun çıkarmaz)
SUPPORT_CHANNEL = ""
# Grup linkin sabit:
SUPPORT_GROUP = "https://t.me/Pars_Sohbet_TR"

# =========================
# Spotify API (opsiyonel)
# =========================
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "")

# =========================
# ✅ YouTube API KEY (senin key’in)
# =========================
YOUTUBE_API_KEY = "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So"
# İstersen environment üzerinden de kullanmak için:
os.environ["YOUTUBE_API_KEY"] = YOUTUBE_API_KEY

# =========================
# Limitler/Playlist
# =========================
VIDEO_STREAM_LIMIT = int(getenv("VIDEO_STREAM_LIMIT", "3"))
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "100"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "50"))

# =========================
# Clean Mode
# =========================
CLEANMODE_DELETE_MINS = int(getenv("CLEANMODE_MINS", "30"))

# =========================
# Telegram Dosya Limitleri (bayt)
# =========================
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600"))   # 100MB
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1073741824"))  # 1GB

# =========================
# Otomatik Komut Kurulumu
# =========================
SET_CMDS = getenv("SET_CMDS", "False")

# =========================
# String Sessions (opsiyonel)
# =========================
STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", "")
STRING3 = getenv("STRING_SESSION3", "")
STRING4 = getenv("STRING_SESSION4", "")
STRING5 = getenv("STRING_SESSION5", "")

# =========================
# Asistan/Auto Ayarlar (opsiyonel)
# =========================
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "false")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "5400"))
AUTO_SUGGESTION_TIME = int(getenv("AUTO_SUGGESTION_TIME", "5400"))
AUTO_SUGGESTION_MODE = getenv("AUTO_SUGGESTION_MODE", None)
AUTO_DOWNLOADS_CLEAR = getenv("AUTO_DOWNLOADS_CLEAR", None)

# Private bot modu (opsiyonel)
PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", None)

# İndirme ekran güncelleme gecikmeleri
YOUTUBE_DOWNLOAD_EDIT_SLEEP = int(getenv("YOUTUBE_EDIT_SLEEP", "3"))
TELEGRAM_DOWNLOAD_EDIT_SLEEP = int(getenv("TELEGRAM_EDIT_SLEEP", "5"))

# =========================
# Görseller
# (HTTP(S) ile başlamazsa ArchMusic exit veriyordu; hepsini https yaptık)
# =========================
START_IMG_URL = getenv("START_IMG_URL", "https://telegra.ph/file/cc8c09f1a7de0b191c2b7.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://telegra.ph/file/cc8c09f1a7de0b191c2b7.jpg")
PLAYLIST_IMG_URL = getenv("PLAYLIST_IMG_URL", "https://telegra.ph/file/cc8c09f1a7de0b191c2b7.jpg")

GLOBAL_IMG_URL = getenv("GLOBAL_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
STATS_IMG_URL = getenv("STATS_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
TELEGRAM_AUDIO_URL = getenv("TELEGRAM_AUDIO_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
TELEGRAM_VIDEO_URL = getenv("TELEGRAM_VIDEO_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
STREAM_IMG_URL = getenv("STREAM_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
SOUNCLOUD_IMG_URL = getenv("SOUNCLOUD_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
YOUTUBE_IMG_URL = getenv("YOUTUBE_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
SPOTIFY_ARTIST_IMG_URL = getenv("SPOTIFY_ARTIST_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
SPOTIFY_ALBUM_IMG_URL = getenv("SPOTIFY_ALBUM_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")
SPOTIFY_PLAYLIST_IMG_URL = getenv("SPOTIFY_PLAYLIST_IMG_URL", "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small")

# =========================
# Görsel URL doğrulama (ArchMusic exit atmasın diye)
# =========================
def _check_url(name, value, allow_asset=False, asset_name=None):
    if allow_asset and value == asset_name:
        return
    if value and not re.match(r"(?:http|https)://", value):
        print(f"[ERROR] - {name} url must start with https://")
        sys.exit()

_check_url("UPSTREAM_REPO", UPSTREAM_REPO)
_check_url("GITHUB_REPO", GITHUB_REPO)
if SUPPORT_CHANNEL:
    _check_url("SUPPORT_CHANNEL", SUPPORT_CHANNEL)
if SUPPORT_GROUP:
    _check_url("SUPPORT_GROUP", SUPPORT_GROUP)

_check_url("START_IMG_URL", START_IMG_URL)
_check_url("PING_IMG_URL", PING_IMG_URL)
_check_url("PLAYLIST_IMG_URL", PLAYLIST_IMG_URL)
_check_url("GLOBAL_IMG_URL", GLOBAL_IMG_URL)
_check_url("STATS_IMG_URL", STATS_IMG_URL)
_check_url("TELEGRAM_AUDIO_URL", TELEGRAM_AUDIO_URL)
_check_url("TELEGRAM_VIDEO_URL", TELEGRAM_VIDEO_URL)
_check_url("STREAM_IMG_URL", STREAM_IMG_URL)
_check_url("SOUNCLOUD_IMG_URL", SOUNCLOUD_IMG_URL)
_check_url("YOUTUBE_IMG_URL", YOUTUBE_IMG_URL)
_check_url("SPOTIFY_ARTIST_IMG_URL", SPOTIFY_ARTIST_IMG_URL)
_check_url("SPOTIFY_ALBUM_IMG_URL", SPOTIFY_ALBUM_IMG_URL)
_check_url("SPOTIFY_PLAYLIST_IMG_URL", SPOTIFY_PLAYLIST_IMG_URL)

# =========================
# Diğer Sabitler
# =========================
AYU = ["💞", "🦋", "🔍", "🧪", "⚡️", "🔥", "🎩", "🌈", "🍷", "🥂", "🥃", "🕊️", "🪄", "💌", "🧨"]
STICKERS = [
    "CAACAgUAAx0Cd6nKUAACASBl_rnalOle6g7qS-ry-aZ1ZpVEnwACgg8AAizLEFfI5wfykoCR4h4E",
    "CAACAgUAAx0Cd6nKUAACATJl_rsEJOsaaPSYGhU7bo7iEwL8AAPMDgACu2PYV8Vb8aT4_HUPHgQ",
]

# ArchMusic bazı yerlerde bunları import ediyor
BANNED_USERS = filters.user()
YTDOWNLOADER = 1
LOG = 2
LOG_FILE_NAME = "ParsMuzik.log"  # logging.py bunun peşindeydi

adminlist = {}
lyrical = {}
chatstats = {}
userstats = {}
clean = {}
autoclean = []

# =========================
# Süre yardımcıları
# =========================
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
SONG_DOWNLOAD_DURATION_LIMIT = int(time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00"))

# =========================
# ASCII Bot Adı kontrolü (ArchMusic kuralı)
# =========================
if not MUSIC_BOT_NAME.isascii():
    print("[ERROR] - MUSIC_BOT_NAME must be ASCII characters only!")
    sys.exit()
