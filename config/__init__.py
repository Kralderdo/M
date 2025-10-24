# -*- coding: utf-8 -*-
import re
import sys
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Telegram API
API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")

# Bot Token
BOT_TOKEN = getenv("BOT_TOKEN", "")

# MongoDB
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

# Bot Owner
OWNER_ID = list(map(int, getenv("OWNER_ID", "").split()))

# Log Grubu
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "0"))

# Bot İsmi
MUSIC_BOT_NAME = getenv("MUSIC_BOT_NAME", "ParsMüzikBot")

# Heroku Ayarları
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")

# Repo Update
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", "")

# Destek Linkleri (boş geçilebilir)
SUPPORT_CHANNEL = ""
SUPPORT_GROUP = ""

# Süre Limitleri
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "180"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))

# YouTube API Key ✅ senin key ile
YOUTUBE_API_KEY = "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So"

# Bot Limit Ayarları
VIDEO_STREAM_LIMIT = int(getenv("VIDEO_STREAM_LIMIT", "3"))
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "100"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "50"))

# Temizlik Modu
CLEANMODE_DELETE_MINS = int(getenv("CLEANMODE_MINS", "30"))

# Telegram Dosya Sınırları
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1073741824"))

# Spotify API
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "")

# String Sessions
STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", "")
STRING3 = getenv("STRING_SESSION3", "")
STRING4 = getenv("STRING_SESSION4", "")
STRING5 = getenv("STRING_SESSION5", "")

# Eksik değişken FIX ✅ (botun çökme sebebi bunlardı)
LOG_FILE_NAME = "logs.txt"
PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", None)
adminlist = {}
lyrical = {}
chatstats = {}
userstats = {}
clean = {}
autoclean = []

# Playlist Image FIX
PLAYLIST_IMG_URL = "https://telegra.ph/file/cc8c09f1a7de0b191c2b7.jpg"

# Ban Sistemi
BANNED_USERS = filters.user()

# Süre dönüştürücü
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")
SONG_DOWNLOAD_DURATION_LIMIT = time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00")
